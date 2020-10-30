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
# from core.detection.camera import VideoCamera
from core.debug_tools.timer import Timer
from core.debug_tools.fps import FPS


from core.detection.face_embedder import FaceEmbedder
from core.detection.face_recognizer import FaceRecognizer
from core.detection.video_camera import VideoCamera

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

# MODELS
face_embedder = FaceEmbedder()
face_detector = FaceRecognizer(PATH_TO_FACE_DETECTION_MODEL)

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
client = FractalClient("213.161.242.88", 9876, FractalReader())
client.set_queues(disp_que, recv_que)
client.init()
time.sleep(.1)

# Connect to the server
disp_que.add_response({"response_name": "gate_authorization"})

def generateStringUUID():
    return str(uuid.uuid4())


session_id = generateStringUUID()


speed_timer = None

@app.on_event("shutdown")
def shutdown_event():
    client.close_client()

def frame_generator():
    
    face_timer = Timer(countdown=3)

    global speed_timer

    SHOW_FACE = True
    
    while True:

        frame = cam.get_frame()
        face_boxes = face_detector.predict_faces(frame)

        for face_box in face_boxes:


            if VideoCamera.valid_size(face_box):

                face_timer.start()

                if face_timer.is_expired():
                    
                    face_crop = cam.crop_frame(face_box)        
                    face_emb = face_embedder.frame_to_embedding(face_crop)
                    face_emb = face_emb.tolist()[0]

                    # SAVE LOCALLY
                    cam.save_thumbnail(frame, face_box, session_id)

                    disp_que.add_response(
                        {"response_name": "user_authorization",
                        "embedding": face_emb, 
                        "session_id": session_id})

                    """ STOPS TIMER, THEREFORE ONLY 1 EMBEDDING SENT """
                    face_timer.stop()

                    # START SPEED_TEST TIMER
                    speed_timer = time.time()
            else:
                face_timer.restart()

            if SHOW_FACE:
                frame = VideoCamera.draw_rectangle(frame, face_box)

        frame_bytes = VideoCamera.frame_to_bytes(frame)
        yield (b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")


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

    print("Session ID: ", session_id)
    global speed_timer
    try:
        while True:
            try:
                # TIMER
                stop_timer = False

                msg = recv_que.get_response()
                recv_que.confirm_sent()
                if (msg["name"] == "user_unidentified"):

                    # SEND TO REMOTE
                    session = msg["data"]["session_id"]
                    disp_que.add_response(
                        {"response_name": "user_thumbnail",
                        "thumbnail_path": "./static/images/tmp/" + session + ".jpg",
                        "session_id": session})
                    
                    # SHOW LOCALLY
                    path = msg["data"]["qr_path"]
                    await websocket.send_json({"thumbnail_path": path})

                    stop_timer = True # TIMER

                elif (msg["name"] == "user_identified"):
                    # SHOW LOCALLY
                    path = msg["data"]["thumbnail_path"]
                    await websocket.send_json({"thumbnail_path": path})
                    stop_timer = True


                if stop_timer:
                    # STOP SPEED_TEST TIMER
                    stop = time.time() - speed_timer
                    print("Took (s): ", str(stop))


            except queue.Empty:
                pass  # LOL :P
            await asyncio.sleep(0.0005)

    except WebSocketDisconnect:
        await websocket.close(code=1000)
