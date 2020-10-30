from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
import time
import json
import pickle
import qrcode
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class Cam:
    pass

class FaceDetect:
    pass

class FaceEmbedd:
    pass

class Client:
    pass

cam = Cam()
client = Client()
detector = FaceDetect()
embedder = FaceEmbedd()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>

        <li id="step1">false</li>
        <li id="step2">false</li>
        <li id="step3">false</li>
        <img id="thumbnail" src="/static/images/thumbnail.png">

        <script>

        var img_is_qr = false;

        var setImg = function(path) {
            if(!img_is_qr) {
                document.getElementById("thumbnail").src = path;
                img_is_qr = true;
            }
        };


        var ws = new WebSocket("ws://localhost:8000/ws");

        // RECEVING PART

        ws.onmessage = function(event) {
            var states = JSON.parse(event.data)
            //console.log(states)
            //console.log("IMGPATH: ", states.img_path)
            document.getElementById("step1").innerHTML = states.step1;
            document.getElementById("step2").innerHTML = states.step2;
            document.getElementById("step3").innerHTML = states.step3;
            setImg(states.img_path)
        };

        // SENDING PART
        function sendMessage(event) {
            var input = document.getElementById("messageText")
            ws.send(input.value)
            input.value = ''
            event.preventDefault()
        }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)

def create_payload():
    pass

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()

#     cam = Cam()
#     client = Client()
#     client.payload

#     detector = FaceDetect()
#     embedder = FaceEmbedd()

#     wait_for_msg = False
#     timer_has_expired = False
#     face_found = False


#     while True:
#         # Recieve from WebClient

#         img = cam.read()
#         face_box = detector(img)
#         face_img = cam.roi(face_box)

#         if face_found:
#             if timer_has_expired:

#                 await websocket.send_text(face_found)

#                 face_emb = embedder(face_img)
#                 client.payload = create_payload(face_emb)

#                 await websocket.send_text(data)


#         yield (b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" + img + b"\r\n")


#         data = await websocket.receive_text()

#         await websocket.send_text(data)

@app.get("/entered")
async def entered_gate():
    """ kinda resets temp-stuff when user have entered the gate"""
    # remove /static/images/tmp/face.jpg
    # remove /static/images/tmp/qr.jpg
    return "Done"

@app.post("/qr/{URL}")
def update_qr(input: str):
    """ accepts URL, creates then returns a QR-Code (.jpg) """
    img_path = "static/images/tmp/"
    img_name = "qr.jpg"
    file_loc = img_path + img_name

    img = qrcode.make(data=input)
    img.save(img_path + img_name)
    return {"file_path": file_loc}

# @app.put("/qr/{url}", response_class=PlainTextResponse)
# async def create_QR(url: str):
#     """ accepts URL, creates then returns a QR-Code (.jpg) """
#     # Returns a cv2 image array from the document vector
#     img_path = "static/images/tmp/"
#     img_name = "qr.jpg"
#     img = qrcode.make(data=url)
#     file_loc = img_path + img_name

#     img.save(img_path + img_name)
#     return file_loc

@app.get("/embedding/{img_path}")
async def get_validation(face_img):
    """ accepts URL, and returns a QR-Code (.jpg) """
    img = cv2.imread(img_path)
    embedding = embedder.img_to_embedding(img)
    return {
        "payload_name": "user_authorization",
        "segments": [],
        "json_payload": {
            "session_id": "RANDOM ID",
            "face_features": embedding
        }
    }



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    stuff = {
        "step1": True,
        "step2": True,
        "step3": False,
        "img_path": "/static/images/tmp/qr_test.jpg"
    }

    # TEST_URL = ""

    while True:
        # file_path = await requests.get(f"/qr/{TEST_URL}")
        await websocket.send_json(stuff)
        data = await websocket.receive()



        # data = await websocket.receive_text()
        # Recieve from WebClient
        # data = await websocket.receive_text()


"""

if faces_size > 300x300 pixels
    if timer > 0.5 seconds
        ' take photo '
        embedd = FaceEmbedd( 'photo' )

IS_FACE_FOUND: bool
IS_FACE_VALID: bool
IS_ACCESS_YES = IS_FACE_FOUND & IS_FACE_VALID

while True:

    frame = cam.read()
    faces = FaceDetect(frame)

    if faces_size > 300x300 pixels            # big enough
        if timer > 0.5 seconds                # safety
            embed = FaceEmbedd(faces)

    await remote_client.recv()


    embed = FaceEmbedd(faces)






    yield (b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" + frame + b"\r\n")



TWO THREADS

SYSTEM_COMMANDS = {
    "FACE_READY": False,
    "FIND_FACES": False,
    "FACE_FOUND": False,
    "EMBED_READY": False
}

video_camera():
    while True:
        frame = cap.read()
        bbox = detector(frame)
        face = roi(bbox)
        if bbox > valid_img_size:
            if time > countdown:
                # save to end-point
                cv2.imwrite("face.jpg", face)
                notify other thread
        yield --frame--


@app.get(/validate)
def validate():

    img = request.get("/face")
    emb = img_to_embedding(img)
    payload = create_payload(emb)
    send_payload(payload)

    response = client.recieve()

    if response["payload_name"] = "user_identified":
        access_granted: true/false
        thumbnail: bytes [4096]
        # TODO: Show access approved
        # TODO: Show thumbnail

    elif response["payload_name"] = "user_unidentified":
        registration_url: "fractal.com/registration?token=123abc666"
        # TODO: Show access declined
        # TODO: Show create QR-Code
        # TODO: Show QR-Code



    IF ENTERED or registration_confirmed:
        " User have entered the gate "
        # GOTO: Start







CAM THREAD>



































"""