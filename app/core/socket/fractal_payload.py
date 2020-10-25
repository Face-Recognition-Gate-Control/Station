from .stream_constants import PAYLOAD_LENGTH, SEGMENTS_LENGTH, BYTE_ORDER, PAYLOAD_NAME_LENGTH, ENCODING, JSON_LENGTH
from .fractal_segment import Segment
from .stream_helper import Send_function
import json

TMP_DIR = "./tmp/"

class RecievedPayload:
    def __init__(self, payload_name, payload_data, segments):
        self.payload_name = payload_name
        self.payload_data = payload_data
        self.segments = segments

class Payload:
    def __init__(self, payload_name: str):
        self.payload_name = payload_name
        self.segments = {}
        self.json_body = "{}"

    # Adds a segment to the payload
    def add_segment(self, name: str, segment: Segment):
        self.segments[name] = segment

    # Adds json string data payload: string from json.dumps
    def add_json_data(self, json_string):
        self.json_body = json_string

    # Writes the payload to the stream of the socket
    def write_to_stream(self, send_all: Send_function):
        # HOLDS TOTAL PAYLOAD SIZE
        total_payload_size = 0

        # PAYLOAD NAME
        payload_name_length = len(self.payload_name)
        payload_name_bytes_size = payload_name_length.to_bytes(
            PAYLOAD_NAME_LENGTH, BYTE_ORDER)
        payload_name_bytes = bytes(self.payload_name, ENCODING)

        total_payload_size += payload_name_length

        # SEGMENTS SIZE AND META
        segments = []
        segment_size = 0
        for (segment_identifier, segment) in self.segments.items():
            segments.append({segment_identifier: segment.get_meta()})
            segment_size += segment.get_segment_size()
            total_payload_size += segment.get_segment_size()
        # print(f"TOTAL SEGMENT SIZE ", segment_size)
        # PARSE META TO JSON AND GET LENGTH
        segment_json = json.dumps(segments)
        segment_meta_length = len(segment_json)
        segment_meta_byte_size = segment_meta_length.to_bytes(
            SEGMENTS_LENGTH, BYTE_ORDER)
        segment_meta_bytes = bytes(segment_json, ENCODING)

        total_payload_size += segment_meta_length

        # JSON BODY
        json_body_length = len(self.json_body)
        json_body_byte_size = json_body_length.to_bytes(
            JSON_LENGTH, BYTE_ORDER)
        json_body_bytes = bytes(self.json_body, ENCODING)
        total_payload_size += json_body_length

        total_payload_bytes = total_payload_size.to_bytes(
            PAYLOAD_LENGTH, BYTE_ORDER)

        ## START WRITING ##

        # TOTAL PAYLOAD SIZE
        send_all(total_payload_bytes)

        # PAYLOAD NAME SIZE
        send_all(payload_name_bytes_size)
        # PAYLOAD NAME
        send_all(payload_name_bytes)

        # SEGMENT META SIZE
        send_all(segment_meta_byte_size)
        # SEGMENT META
        send_all(segment_meta_bytes)

        # JSON f
        send_all(json_body_byte_size)
        # JSON DATA
        send_all(json_body_bytes)

        # SEGMENTS
        for segment in self.segments.values():
            segment.write_to_stream(send_all)

if __name__ == "__main__":
    """ TEST STUFF BELOW """