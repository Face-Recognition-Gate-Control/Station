
""" MODELS """
face_detector = None
face_embedder = None

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

def pseudo_camera_loop():
    """
    Responseibility:
    
    Read information from the camera and act accordingly.
    This means, either:
                        Find Face
                        Save Face
                        Make Face-embedding.
    
    """    
    while True:

        frame = cam.get_frame()
        face_boxes = face_detector.predict_faces(frame)

        for face_box in face_boxes:
            if VALIDATE_FACE:
                if valid_face_size(face_box):
                    cam_timer.start()
                    if cam_timer.is_expired():
                        face = cam.get_roi(face_box)
                        cv2.imwrite("./tmp/face.jpg", face)
                        embedding = face_embedder.frame_to_embedding(face)
                        disp_que.add_response({
                            "response_name": "user_authorization",
                            "embedding": embedding
                        })
                        start_confirmation_timer_from_server()
                else:
                    cam_timer.stop()

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
    
        msg = recv_que.get_response()
        
        await websocket.send_json({
            "msg": msg
        })
        recv_que.confirm_sent()

