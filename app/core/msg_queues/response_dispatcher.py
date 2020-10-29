from core.socket.fractal_segment import JsonSegment, FileSegment
from core.socket.fractal_payload import Payload
import queue
import json


class ResponseDispatcher:

    def __init__(self):
        self.que = queue.Queue()

    def add_response(self, response):
        """ Add payloads to be sent by the client"""
        # print("Added: ", response)
        self.que.put(response)

    def get_response(self):
        """ Gets response ready to be handled """
        return self.que.get(timeout=0.0005)

    def confirm_sent(self):
        self.que.task_done()

    def shutdown(self):
        self.que.join()

    def is_empty(self):
        return self.que.empty()

    @staticmethod
    def create_payload_response(response):
        payload = None
        try:
            response_name = response["response_name"]
            print(f"SEND: response [type: {response_name}]")

            if response_name == "gate_authorization":
                payload = Payload("gate_authorization")
                gate_info = {
                    "login_key": "secret",
                    "station_uid": "10000000-0000-0000-0000-000000000000"
                }
                payload.add_json_data(json.dumps(gate_info))

            elif response_name == "gate_ping":
                payload = Payload("gate_ping")

            elif response_name == "user_authorization":
                # requires the server to validate the face features for validation.
                payload = Payload("user_authorization")
                payload.add_json_data(json.dumps({
                    "session_id": response["session_id"],
                    "face_features": response["embedding"]
                }))

            elif response_name == "user_thumbnail":
                # send thumbnail (send face crop to database)
                payload = Payload("user_thumbnail")
                payload.add_json_data(json.dumps(
                    {"session_id": response["session_id"]}))
                payload.add_segment("thumbnail", FileSegment(
                    open(response["thumbnail_path"], "rb")))


            elif response_name == "user_entered":
                """ COUNTDOWN FOR LIKE 10 SECONDS?? """
                payload = Payload("user_entered")
                payload.add_json_data(json.dumps(
                    {"session_id": "ID from authorization"}))

            else:
                print("Couldn't create payload")

        except KeyError as ke:
            print("Found no matching response for the given payload")
            print(ke)

        return payload
