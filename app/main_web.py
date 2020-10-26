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

# DEBUG TOOLS
debug_timer = Timer(countdown=3)
debug_fps = FPS()


@app.on_event("shutdown")
def shutdown_event():
    client.close_client()

def frame_generator():
        debug_timer.start()
        while True:
            frame = cam.get_frame()
            if debug_timer.is_expired():
                disp_que.add_response({"response_name": "gate_ping"})
                debug_timer.restart()
            
            # print(debug_fps())
            yield (b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" + frame + b"\r\n")

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
    
    try:
        while True:
            try:
                msg = recv_que.get_response()
                await websocket.send_json(test_payload)
                recv_que.confirm_sent()
            except queue.Empty:
                pass # LOL :P
            await asyncio.sleep(0.015)
    except WebSocketDisconnect:
        await websocket.close(code=1000)

