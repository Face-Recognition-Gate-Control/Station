from .stream_helper import Send_function
from .stream_constants import ENCODING
from io import BufferedReader
import mimetypes
import abc
import os
from typing import Callable, NewType

# Holder class for received payloads, includes payload data< JSON and
# segments< Files
class Segment(metaclass=abc.ABCMeta):

    _META_KEY_SIZE = "size"
    _META_KEY_MIME_TYPE = "mime_type"
    _META_KEY_FILE_NAME = "file_name"

    def __init__(self):
        super().__init__()
        self.segment_meta = {}

    @abc.abstractmethod
    def write_to_stream(self, send_function: Send_function):
        pass

    def get_segment_size(self):
        return self.segment_meta.get(self._META_KEY_SIZE)

    def get_meta(self):
        return self.segment_meta

    def set_segment_size(self, size: int):
        self.segment_meta[self._META_KEY_SIZE] = size

    def set_segment_mime_type(self, mimeType: str):
        self.segment_meta[self._META_KEY_MIME_TYPE] = mimeType

    def set_segment_file_name(self, file_name: str):
        self.segment_meta[self._META_KEY_FILE_NAME] = file_name

class RecivedSegment:
    def __init__(self, segment_meta, file_name):
        self.segment_meta = segment_meta
        self.file_name = file_name

class JsonSegment(Segment):

    def __init__(self, json_string: str):
        super().__init__()
        self.json_string = json_string
        self.set_segment_size(len(json_string))
        self.set_segment_mime_type("application/json")

    def write_to_stream(self, send_function: Send_function):
        send_function(bytes(self.json_string, ENCODING))

class FileSegment(Segment):
    def __init__(self, file: BufferedReader):
        super().__init__()
        self._file = file
        self.set_segment_size(os.path.getsize(file.name))
        self.set_segment_mime_type(mimetypes.guess_type(file.name)[0])
        file_name = file.name.split("/")
        self.set_segment_file_name(file_name[-1])

    def write_to_stream(self, send_function: Send_function):
        reader = self._file.read(256)
        while (reader):
            send_function(reader)
            reader = self._file.read(256)
        self._file.close()

if __name__ == "__main__":

    file_path = "static\images\scott.png"
    fs = FileSegment(open(file_path, "rb"))
    
    print(fs.read())