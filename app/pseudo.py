from core.debug_tools.timer import Timer
from core.detection.camera import VideoCamera
import cv2
import torch

""" MODELS """
face_detector = None
face_embedder = None


""" PAYLOAD TESTS """
# [gate_authorization]   Success
# [user_authorization]   Success
# [user_unidentified]    Success
# [user_identified]      Success
# [gate_ping / pong]     Success

""" OTHER TEST """
# (show QR.jpg )         Success
# (show thumgnail.jpg)   Success
# (website registration) Success      

""" NOT STARTED """
# {simulate user entrence}










""" COMMUNICATION """
client = None
recv_que = None
disp_que = None

""" CONTROL STATES """
cam = None
cam_timer = None
VALIDATE_FACE = None
valid_face_size = None 

""" PROCESS STATES """
IS_SCANNING: bool
IS_VALIDATING: bool
IS_ACCESSED: bool

IS_RESTART: bool
IS_VALIDATING_TAKING_TO_LONG: bool

# DEBUG TOOLS
SHOW_FACE_BOX: bool
"""
Q & A
How long should we wait for answer from server? (if taking too long, -> restart process)

Impl func:
- global timer
- global process-states dict or something
- image saver to ./tmp folder
-       save different sizes?
"""

S_INIT = "INIT"
S_SCANNING = "SCANNING"
S_VALIDATING = "VALIDATING"
S_ACCESS = "ACCESS"

current_state = S_INIT

def pseudo_camera_loop():
    response_timer = Timer(5)    # answer from server
    camera_timer = Timer(3)      # before taking picture of user
    global current_state
    while True:

        frame = cam.get_frame()
        face_boxes = face_detector.predict_faces(frame)
        
           
        for face_box in face_boxes:
            
            current_state = current_state["state"]
            
            if current_state == "SCANNING":
                recv_que.add_repsonse({"state": "SCANNING"})
                current_state = "VALIDATING"
            
            if current_state == "VALIDATING":
                if VideoCamera.valid_size(face_box):
                    camera_timer.start()
                    if camera_timer.is_expired():
                        face = cam.get_roi(face_box)
                        cv2.imwrite("./tmp/imgs/face.jpg", face)
                        embedding = face_embedder.frame_to_embedding(face)
                        disp_que.add_response({
                            "response_name": "user_authorization",
                            "embedding": embedding.tolist()
                        })
                        camera_timer.stop()
                        current_state = "ACCESS"
                else:
                    camera_timer.stop()
            
            if current_state == "ACCESS":
                response_timer.start()
                if response_timer.is_expired():
                    if not msg_from_server:
                        # REMOVE STUFF FROM TEMP FOLDER AND RESET??
                        current_state = "SCANNING"
                        response_timer.stop()
                    else:
                        # WAIT FOR USER TO ENTER GATE??
                        
        
            if SHOW_FACE_BOX:
                frame = VideoCamera.draw_rectangle(frame, face_box)
                
        yield (b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" + frame + b"\r\n")
        


async def pseudo_websocket_loop():
    """
    Responseibility:
    
    Read feeback from server, and act accordingly.
    This means, either:
                        display stuff to GUI
                        change the 'state' of the system e.l.
                        re-send stuff into the que
    
    """   
    websocket = None 
    while True:
        
        data = {}
        response = recv_que.get_response()
        state = response["state"]
        
        if state == "SCANNING":
            data = {
                "state": "SCANNING"
            }
            
        if state == "VALIDATION":
            data = {
                "state": "VALIDATION",
                "access_granted": True,
                "thumbnail_path": response["data"]["thumbnail_path"]
            }
            
        if state == "ACCESS":
            data = {
                "state": "ACCESS",
                "access_granted": False,
                "qr_path": response["data"]["qr_path"]
            }
            
        await websocket.send_json(data)
        recv_que.confirm_sent()


