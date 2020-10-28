import asyncio
import queue
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, WebSocket
from starlette.responses import StreamingResponse
from starlette.websockets import WebSocketDisconnect
# FRACTAL core
from core.msg_queues.response_dispatcher import ResponseDispatcher
from core.msg_queues.response_receiver import ResponseReceiver
from core.socket.fractal_client import FractalClient
from core.socket.fractal_reader import FractalReader
from core.detection.camera import VideoCamera
from core.debug_tools.timer import Timer
from core.debug_tools.fps import FPS


from core.detection.face_embedder import FaceEmbedder
from core.detection.face_recognizer import FaceRecognizer
from core.detection.video_canvas import VideoCanvas
from core.utils.data import compare_embeddings, load_embeddings_to_dict
import numpy as np
import torch
import cv2
import os
import uuid

import time

# TODO: (Idea) Create Configloader?
# TODO: (Idea) Create Dataloader?

# TODO: Where to place this?
PATH_TO_FACE_DETECTION_MODEL = "./static/models/RFB-640/face_model.pth"

# TODO: Where to place this?
# TODO: import local weigths into Embedd-model (be careful inside ML-modules)
PATH_TO_FACE_EMBEDDING_MODEL = "./static/models/InceptionResnetV1/vggface2.pth"

# TODO: Where to place this?
PATH_TO_ANCHORS = "static/images/test_embeddings"
PATH_TO_IMAGES = "static/images/test_images"
PATH_TO_CROPS = "static/images/test_crops"

face_embedder = FaceEmbedder()
face_detector = FaceRecognizer(PATH_TO_FACE_DETECTION_MODEL)

# " DATABASE "
embeddings = load_embeddings_to_dict(PATH_TO_ANCHORS)


# SERVER SETTINGS
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# WEB CAMERA
cam = VideoCamera()


# GLOBAL MESSAGE QUEUES
recv_que = ResponseReceiver()
disp_que = ResponseDispatcher()

# CONNECTION TO REMOTE SERVER
client = FractalClient("localhost", 9876, FractalReader())
client.set_queues(disp_que, recv_que)
client.init()
time.sleep(.1)


# Connect to the server
disp_que.add_response({"response_name": "gate_authorization"})


def generateStringUUID():
    return str(uuid.uuid4())


session_id = generateStringUUID()

# DEBUG TOOLS
debug_timer = Timer(countdown=1)
debug_fps = FPS()


@app.on_event("shutdown")
def shutdown_event():
    client.close_client()


def frame_generator():
    debug_timer.start()
    face_timer = Timer(countdown=3)
    face_timer.start()

    while True:
        frame = cam.read_frame()
        face_boxes = face_detector.predict_faces(frame)

        for face_box in face_boxes:
            if (face_timer.is_expired()):
                x_min, y_min, x_max, y_max = face_box
                crop = frame[int(y_min):int(y_max), int(x_min):int(x_max)]

                face_emb = face_embedder.frame_to_embedding(crop)
                cam.save_frame(frame, f"tmp/imgs/{session_id}.jpg")
                disp_que.add_response(
                    {"response_name": "user_authorization", "embedding": face_emb.tolist()[0], "session_id": session_id})
                face_timer.restart()

        yield (b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" + cam.frame_to_bytes(frame) + b"\r\n")


@app.get("/frame_streamer")
async def frame_streamer():
    return StreamingResponse(
        frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.websocket("/comms")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    test_payload = {"state": "INIT"}

    capture_embedding = True
    print(session_id)

    try:
        while True:
            try:
                msg = recv_que.get_response()
                recv_que.confirm_sent()
                print(msg)
                if (msg["name"] == "user_unidentified"):
                    session = msg["data"]["session_id"]
                    disp_que.add_response(
                        {"response_name": "user_thumbnail", "thumbnail_path": "./tmp/imgs/"+session+".jpg", "session_id": session})
                    await websocket.send_json({"qr": True})
                    capture_embedding = True

                elif (msg["name"] == "user_identified"):
                    print(msg["data"])
                    # disp_que.add_response(
                    #     {"response_name": "user_thumbnail", "thumbnail_path": "./tmp/"+msg["session_id"]+".jpg"})

            except queue.Empty:
                pass  # LOL :P
            await asyncio.sleep(0.015)
    except WebSocketDisconnect:
        await websocket.close(code=1000)
