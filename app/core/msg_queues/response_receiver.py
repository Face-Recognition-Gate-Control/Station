from PIL import Image
import queue
import qrcode


class ResponseReceiver():

    def __init__(self):
        self.que = queue.Queue()

    def add_response(self, response):
        """ Add payloads to be sent by the client"""
        self.que.put(response)

    def get_response(self):
        """ Gets payloads received from the client """
        return self.que.get(timeout=0.015)

    def confirm_sent(self):
        self.que.task_done()

    def shutdown(self):
        self.que.join()

    def is_empty(self):
        return self.que.empty()

    @staticmethod
    def create_response(payload):
        print("Received response")

        response = None
        try:
            payload_type = payload.payload_name

            
            if payload_type == "gate_authorized":
                """ we're registrated as a gate station """
                # does the gate name match ours??
                gate_name = payload["json_payload"]["station_name"]
                if gate_name == "OURS":
                    print("Good shitt")

            elif payload_type == "pong":
                """ server wants to know if we're alive """
                """ our 'ping' was successful """
                print("payload_name: ", payload.payload_name)
                print("payload_data: ", payload.payload_data)
                print("    segments: ", payload.segments)
                response = "HEY FRONTNERDS"
                # Retry on nothing received or extend timer when pong is received

            elif payload_type == "user_identified":
                """ user is identified """
                # we've now received a thumbnail.jpg in ./tmp folder
                response = {
                    "system_state": "access",
                    "message": payload.payload_data["message"],
                    "session_id": payload.payload_data["session_id"],
                    "access_granted": payload.payload_data["access_granted"],
                    "thumbnail_path": payload.segments["thumbnail"]
                }

            elif payload_type == "user_unidentified":
                # user not registrated
                # open the registration_url from response
                # generate QR-CODE and show it in GUI
                # get URL from the response, and generate QR CODE stuff
                TMP_DIR = "./tmp/"
                FILENAME = "qr.jpg"
                QR_PATH = TMP_DIR + FILENAME
                registration_url = payload.payload_data["registration_url"]
                img = qrcode.make(registration_url)
                img.save(QR_PATH)
                response = {
                    "system_state": "validation",
                    "session_id": payload.payload_data["session_id"],
                    "filepath_qr": QR_PATH,
                }
            else:
                # ERROR STUFF
                print("Couldnt create matching response to payload_name")

        except KeyError as ke:
            print("ERROR: No matching key in payload")
            print(ke)

        return response

