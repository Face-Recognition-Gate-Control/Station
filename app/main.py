import asyncio
import queue
import time 
# MODULES
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, WebSocket
from starlette.responses import StreamingResponse
from starlette.websockets import WebSocketDisconnect
# FRACTAL
from core.msg_queues.response_dispatcher import ResponseDispatcher
from core.msg_queues.response_receiver import ResponseReceiver
from core.socket.fractal_client import FractalClient
from core.socket.fractal_reader import FractalReader
from core.debug_tools.timer import Timer
from core.debug_tools.fps import FPS
from core.detection.face_embedder import FaceEmbedder
from core.detection.face_recognizer import FaceRecognizer
from core.detection.video_camera import VideoCamera
from core.utils.session_id import SessionID
from core.utils.command import Command

# SERVER SETTINGS / PATHS
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ML MODELS
face_embedder = FaceEmbedder()
face_detector = FaceRecognizer()

# COMMUNICATION
recv_que = ResponseReceiver()
disp_que = ResponseDispatcher()

# CAMERA SETTINGS
camera = VideoCamera()
camera_timer = Timer(3)

# COMMUNICATION TO REMOTE SERVER
#213.161.242.88
client = FractalClient("10.22.180.90", 9876, FractalReader())
client.set_queues(disp_que, recv_que)
client.init()
time.sleep(.1)

# TEMPORARY STATE MANAGEMENT
camera_command = Command()
session_id = SessionID.get()
is_server_msg_recvd = False      # TO NOTIFY MSG RECEIVED
entrence_timer = Timer(5)        # HOW LONG TO SIMULATE USER ENTERED 
server_timer = Timer(5)          # HOW LONG TO WAIT FROM SERVER
qr_timer = Timer(10)             # HOW LONG TO WAIT FROM SERVER
time.sleep(1)


@app.on_event("startup")
def startup_event():
    # Connect to the server
    disp_que.add_response({"response_name": "gate_authorization"})
    # Starts the camera
    recv_que.add_response({"state": "SCANNING"})

@app.on_event("shutdown")
def shutdown_event():
    client.close_client()
    # CLEAN FOLDERS

def frame_generator():
    while True:
        frame = camera.get_frame()
        face_boxes = face_detector.predict_faces(frame)
        
        for face_box in face_boxes:
            cmd = camera_command()

            if cmd == "IDLE":
                pass

            elif cmd == "SCANNING":
                if VideoCamera.valid_size(face_box):
                    camera_timer.start()
                    if camera_timer.is_expired():
                        on_process_user(frame, face_box)
                        server_timer.start()   # reserver response
                        camera_timer.stop()    # camera trigger
                        camera_command.reset()
                else:
                    camera_timer.restart()
            # SHOW BBOX AROUND FACE
            frame = VideoCamera.draw_rectangle(frame, face_box)

        frame_bytes = VideoCamera.frame_to_bytes(frame)
        yield (b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

@app.websocket("/comms")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        global is_server_msg_recvd
        global session_id
        global global_timer
        while True:

            # EVENT RESTARTS: if no server response
            on_server_timer()
            # EVENT RESTARTS: if entrence granted 
            on_entrence_timer()
            # EVENT RESTARTS: if qr has been opened 
            on_qr_timer()

            display = {"state": "IDLE"}

            try:
                response = recv_que.get_response()
                recv_que.confirm_sent()

                state = response["state"]
                print("[STATE] => ", state)
                if state == "IDLE":
                    pass

                if state == "RESTART":
                    """ RESTART FRONT END"""
                    display["state"] =  "RESTART"
                    session_id = SessionID.get()
                    # Begin scanning again
                    recv_que.add_response({"state": "SCANNING"})
                    # TODO: Clear tmp folder or override?

                if state == "SCANNING":
                    display["state"] = "SCANNING"
                    camera_command.set("SCANNING")
                    is_server_msg_recvd = False # RESET
                    
                if state == "VALIDATION":
                    display["state"] =  "VALIDATION"
                    is_server_msg_recvd = True
                    is_access_granted = response["data"]["access_granted"]
                    session_id = response["data"]["session_id"]
                    if not is_access_granted:
                        disp_que.add_response({
                            "response_name": "user_thumbnail",
                            "thumbnail_path": "./static/images/tmp/" + session_id + ".jpg",
                            "session_id": session_id
                        })
                        # data["message"] = response["data"]["message"] # SHOW or NAH?
                        display["qr_path"] = response["data"]["qr_path"]
                        qr_timer.start()
                    else:
                        state = "ACCESS" # Change state
                    
                if state == "ACCESS":
                    display["state"] =  "ACCESS"
                    display["thumbnail_path"] = response["data"]["thumbnail_path"]
                    # SIMULATE_GATE_ENTRENCE
                    entrence_timer.start()

                if state == "PONG":
                    # TODO: implement
                    # disp_que.add_response({"response_name": "gate_ping"})
                    pass
                
            except queue.Empty:
                pass
            
            # UPDATE (GUI)
            await websocket.send_json(display)
            # NO FREEWHEELING ALLOWED
            await asyncio.sleep(0.015)
            
    except WebSocketDisconnect:
        await websocket.close(code=1000)


@app.get("/frame_streamer")
async def frame_streamer():
    return StreamingResponse(
        frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


""" ---------------------- EVENT HANDLERS ------------------------ """

def on_server_timer():
    if server_timer.is_running():
        if server_timer.is_expired():
            if not is_server_msg_recvd:
                recv_que.add_response({"state": "RESTART"})
            server_timer.stop()
            
def on_qr_timer():
    if qr_timer.is_running():
        if qr_timer.is_expired():
            recv_que.add_response({"state": "RESTART"})
            qr_timer.stop()

def on_entrence_timer():
    if entrence_timer.is_running():
        if entrence_timer.is_expired():
            # NOTIFY SERVER
            print("[ENTERED GATE] User_session_id: ", session_id)
            disp_que.add_response({
                "response_name": "user_entered",
                "session_id": session_id
            })
            recv_que.add_response({"state": "RESTART"})
            entrence_timer.stop()

def on_process_user(frame, face_box):
    # SAVE COPY TO LOCAL TMP FOLDER
    VideoCamera.save_thumbnail(frame, face_box, session_id)
    # EXTRACT FACE
    face_crop = VideoCamera.crop_frame(frame, face_box)
    # GENERATE EMBEDDING
    face_emb = face_embedder.frame_to_embedding(face_crop)
    # TENSOR LIST TO NORMAL LIST
    face_emb = face_emb.tolist()[0]
    # SEND TO SERVER
    disp_que.add_response({
        "response_name": "user_authorization",
        "session_id": session_id,
        "embedding": face_emb
    })
