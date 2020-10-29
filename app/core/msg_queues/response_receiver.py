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
        return self.que.get(timeout=0.0005)

    def confirm_sent(self):
        self.que.task_done()

    def shutdown(self):
        self.que.join()

    def is_empty(self):
        return self.que.empty()

    @staticmethod
    def create_response(payload):

        response = None
        try:
            payload_type = payload.payload_name
            print(f"RECV: response [type: {payload_type}]")

            if payload_type == "gate_authorized":
                """ we're registrated as a gate station """
                # does the gate name match ours??
                gate_name = payload.payload_data["station_name"]
                response = {
                    "name": payload_type,
                    "state": "OTHER",
                    "data": {
                        "gate_name": gate_name
                    }
                }

            elif payload_type == "pong":
                """ server wants to know if we're alive """
                """ our 'ping' was successful """
                print("payload_name: ", payload.payload_name)
                print("payload_data: ", payload.payload_data)
                print("    segments: ", payload.segments)
                response = {
                    "name": payload_type,
                    "state": "OTHER",
                    "data": {
                        "payload_name": payload.payload_name
                    }
                }
                # Retry on nothing received or extend timer when pong is received

            elif payload_type == "user_identified":
                """ user is identified """
                # we've now received a thumbnail.jpg in ./tmp folder
                thumbnail_dir = "./static/images/tmp/" + "thumbnail.jpg"
                response = {
                    "name": payload_type,
                    "state": "VALIDATION",
                    "data": {
                        "session_id": payload.payload_data["session_id"],
                        "message": payload.payload_data["message"],
                        "access_granted": payload.payload_data["access_granted"],
                        "thumbnail_path": thumbnail_dir, #payload.segments["thumbnail"]
                    }
                }

            elif payload_type == "user_unidentified":
                # user not registrated
                # open the registration_url from response
                # generate QR-CODE and show it in GUI
                # get URL from the response, and generate QR CODE stuff
                TMP_DIR = "./static/images/tmp/"
                FILENAME = "qr.jpg"
                QR_PATH = TMP_DIR + FILENAME
                registration_url = payload.payload_data["registration_url"]
                img = qrcode.make(registration_url)
                img.save(QR_PATH)
                response = {
                    "name": payload_type,
                    "state": "VALIDATION",
                    "data": {
                        "session_id": payload.payload_data["session_id"],
                        "access_granted": False,
                        "qr_path": TMP_DIR
                    }
                }
            else:
                print("ERROR: No created response.")

        except KeyError as ke:
            print("ERROR: No matching key in payload")
            print(ke)

        return response


if __name__ == "__main__":


    registration_url = "https://fractal.uials.no"

    TMP_DIR = "../../tmp/imgs/"
    FILENAME = "qr.jpg"
    QR_PATH = TMP_DIR + FILENAME

    img = qrcode.make(registration_url)
    img.save(QR_PATH)