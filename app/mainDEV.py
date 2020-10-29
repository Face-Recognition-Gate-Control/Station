import asyncio
import queue
import time
import uuid
import cv2

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
from core.debug_tools.timer import Timer
from core.debug_tools.fps import FPS

from core.detection.face_embedder import FaceEmbedder
from core.detection.face_recognizer import FaceRecognizer
from core.detection.video_camera import VideoCamera
from core.detection.video_canvas import VideoCanvas
from core.utils.data import compare_embeddings, load_embeddings_to_dict

# SERVER SETTINGS
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
PATH_TO_FACE_DETECTION_MODEL = "./static/models/RFB-640/face_model.pth"

# ML MODELS
face_embedder = FaceEmbedder()
face_detector = FaceRecognizer(PATH_TO_FACE_DETECTION_MODEL)

# COMMUNICATION PIPES
recv_que = ResponseReceiver()
disp_que = ResponseDispatcher()

# CAMERA SETTINGS
camera = VideoCamera()
canvas = VideoCanvas()
camera_timer = Timer(2)

# COMMUNICATION TO REMOTE SERVER
client = FractalClient("213.161.242.88", 9876, FractalReader())
client.set_queues(disp_que, recv_que)
client.init()
ping_timer = Timer(3)     # CHECK IF REMOTE SERVER IS ALIVE
is_server_msg_received = False   # TO NOTIFY MSG RECEIVED
from_server_timer = Timer(5) # HOW LONG TO WAIT FROM SERVER


# TODO: some state management stuff
current_state = "IDLE"

def generateStringUUID():
    return str(uuid.uuid4())


current_session_id = generateStringUUID()

# DEBUG
DISPLAY_FACE_BOX = False


def frame_generator():
    global current_state
    global DISPLAY_FACE_BOX
    
    while True:

        frame = camera.get_frame()
        face_boxes = face_detector.predict_faces(frame)

        for face_box in face_boxes:

            if current_state == "IDLE":
                # TODO: What happens here?
                pass

            if current_state == "TEST":
                ping_timer.start()
                if ping_timer.is_expired():
                    disp_que.add_repsonse({"response_name": "gate_ping"})
                    ping_timer.restart()

            if current_state == "SCANNING":
                recv_que.add_repsonse({"state": "SCANNING"}) # NOTIFY FRONT END (NB: recv_que)
                if VideoCamera.valid_size(face_box):
                    camera_timer.start()
                    if camera_timer.is_expired():
                        face = camera.get_roi(face_box)
                        # TODO: Fix TMP Folder
                        cv2.imwrite("./tmp/imgs/face.jpg", face)
                        embedding = face_embedder.frame_to_embedding(face)
                        disp_que.add_response({
                            "response_name": "user_authorization",
                            "embedding": embedding.tolist()
                        })
                        camera_timer.stop()
                        # Change state, and wait for validation
                        current_state = "VALIDATING"
                else:
                    camera_timer.restart()

            if current_state == "VALIDATING":
                from_server_timer.start()
                if from_server_timer.is_expired():
                    global is_server_msg_received
                    if not is_server_msg_received:
                        # TODO: Clear TMP folder
                        recv_que.add_repsonse({"state": "RESTART"})
                        current_state = "IDLE"
                    else:
                        current_state = "ACCESS"
                    from_server_timer.stop()
            
            if current_state == "ACCESS":
                # WE WAIT FOR USER TO ENTER THE GATE
                # SIMULATE WITH LIKE 5 seconds ??
                # TIMER TO SIMULATE USER HAVE ENTERED ??
                pass

            if DISPLAY_FACE_BOX:
                frame = VideoCanvas.draw_rectangle(frame, face_box)

        frame_bytes = VideoCamera.frame_to_bytes(frame)
        yield (b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

@app.websocket("/comms")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global current_state
    entrence_timer = Timer(5)
    try:
        while True:
            try:
                data = {"state": "DEFAULT"}

                response = recv_que.get_response()
                state = response["state"]

                if state == "SCANNING":
                    """ SIGNALS CAMERA IS SCANNING"""
                    data["state"] =  "SCANNING"
                    
                if state == "VALIDATION":
                    """ STARTS REGISTRATION, or redirects to ACCESS """
                    data["state"] =  "VALIDATION"
                    is_access_granted = response["data"]["access_granted"]
                    if not is_access_granted:
                        data["access_granted"] = False
                        data["message"] = response["data"]["message"] # NOT ALLOWS BECAUSE OF CORONA
                        data["qr_path"] = response["data"]["qr_path"]
                    else:
                        state = "ACCESS" # Change state
                    
                if state == "ACCESS":
                    """ USER CAN NOW ENTER """
                    data["state"] =  "ACCESS"
                    data["access_granted"] = True
                    data["thumbnail_path"] = response["data"]["thumbnail_path"]

                    state = "SIMULATE_GATE_ENTRENCE"

                if state == "SIMULATE_GATE_ENTRENCE":
                    entrence_timer.start()
                    while True:
                        if entrence_timer.is_expired():
                            disp_que.add_response({
                                "response_name": "user_entered",
                                "session_id": current_session_id
                            })
                            entrence_timer.stop()
                            break

                        # RESUME SCANNING
                        state = "RESTART"

                if state == "PONG":
                    """ SIGNALS THAT THE SERVER RECEIVED OUR PING AND REPONDED """
                    # TODO: RESET GATE_PING_TIMER, and retry in 3 minutes?
                    pass
                
                if state == "RESTART":
                    """ RESTART FRONT END"""
                    data["state"] =  "RESTART"

                if state == "DEFAULT":
                    """ NOTHING """
                    pass

                await websocket.send_json(data)
                recv_que.confirm_sent()
                
            except queue.Empty:
                pass
            await asyncio.sleep(0.015)
    except WebSocketDisconnect:
        await websocket.close(code=1000)

@app.on_event("shutdown")
def shutdown_event():
    client.close_client()

@app.get("/frame_streamer")
async def frame_streamer():
    return StreamingResponse(
        frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("indexDEV.html", context={"request": request})