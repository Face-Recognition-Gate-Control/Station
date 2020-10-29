from .stream_helper import read_int, read_bytes_to_string, Recieve_function
from .fractal_payload import RecievedPayload
from .fractal_segment import RecivedSegment, Segment
import json
import uuid

TMP_DIR = "./static/images/tmp/"

class FractalReader:
    # RESPONSIBLE FOR READING DATA FROM SERVER
    # Reads the full payload from the stream of the provided byte stream read function.
    # It returns the payload when it is finished reading
    # THIS IS BLOCKING
    def read(self, reciever: Recieve_function):
        # Length of paylaod in bytes
        payload_length = read_int(reciever)

        # Read payload name length
        payload_name_length = read_int(reciever)

        # Read payload name
        payload_name = read_bytes_to_string(
            reciever, payload_name_length)

        # Read segments length
        segment_length = read_int(reciever)
        # Read segments
        segments = read_bytes_to_string(
            reciever, segment_length)

        # Read JSON payload length
        json_length = read_int(reciever)

        # Read JSON payload
        json_data = read_bytes_to_string(
            reciever, json_length)

        # parse JSON payload data
        payload_data = json.loads(json_data)

        # parse segment JSON payload data
        parsed_segments = json.loads(segments)

        return RecievedPayload(payload_name, payload_data, self.readSegments(reciever, parsed_segments))

    # Reads the actual file segments parsed from header, and builds
    # the dictionary for it to retrieve the files with provided meta data.
    def readSegments(self, reciever, parsed_segments):
        segmentDict = {}
        for segment in parsed_segments:
            segment_key = next(iter(segment.keys()))
            segment_meta = next(iter(segment.values()))
            size = int(segment_meta["size"])
            file_name = ""
            if Segment._META_KEY_FILE_NAME in segment_meta:
                file_name = segment_meta[Segment._META_KEY_FILE_NAME]
            else:
                file_name = str(uuid.uuid1())

            file_name = "thumbnail.jpg"
            file_full_path = TMP_DIR + file_name
            tempt_segment_file = open(TMP_DIR + file_name, 'wb')
            buffer = 4096
            remaining = size
            received_bytes = reciever(min(buffer, remaining))
            while (received_bytes):
                remaining -= len(received_bytes)
                tempt_segment_file.write(received_bytes)
                received_bytes = reciever(min(buffer, remaining))
            tempt_segment_file.close()
            segmentDict[segment_key] = RecivedSegment(
                segment_meta, file_full_path)
        return segmentDict


if __name__ == "__main__":
    """ TEST STUFF BELOW """