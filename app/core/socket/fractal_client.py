from os import terminal_size
from threading import Thread
import socket
import queue

# RESPONSIBLE FOR CONNECTION TO SERVER
class FractalClient():
    def __init__(self, host: str, port: int, reader):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dispatch_que = None
        self.recieve_que = None
        self.is_running = False
        self.connection = False
        self.reader = reader
        self.host = host
        self.port = port
        self.queue_handlers = []
        self.connect()
        
    def set_queues(self, dispatch_que, recieve_que):
        self.dispatch_que = dispatch_que
        self.recieve_que = recieve_que

    def _kill_threads(self):
        for thread in self.queue_handlers:
            thread.join()

    def init(self):
        if not self.connection:
            raise Exception("Socket is not connected")
        elif not self.dispatch_que or not self.recieve_que:
            raise Exception("Queues are not initialized")
        else:
            # TODO: Create 'Client-handler'
            send_thread = Thread(target=self.start_sender)
            read_thread = Thread(target=self.start_reader)
            self.queue_handlers.append(read_thread)
            self.queue_handlers.append(send_thread)
            
            """
            Setting deamon True so we can exit
            main-thread with CTRL+C, and deamons will die eventually
            """
            read_thread.setDaemon(True)
            send_thread.setDaemon(True)

            read_thread.start()
            send_thread.start()
            print("Client initialized.")

    def start_reader(self):
        while self.is_connected():
            try:
                payload = self.read_payload()
                response = self.recieve_que.create_response(payload)
                self.recieve_que.add_response(response)
            except AttributeError as ae:
                print(ae)
                print("Recv-Queue might not have been initialized")

    def start_sender(self):
        while self.is_connected():
            try:
                response = self.dispatch_que.get_response()
                payload = self.dispatch_que.create_payload_response(response)
                self.send_payload(payload)
                self.dispatch_que.confirm_sent()
            except queue.Empty:
                pass # LOL :P 
            except AttributeError as ae:
                print(ae)
                print("Disp-Queue might not have been initialized")

    # Sends the payload to the server
    def send_payload(self, payload):
        payload.write_to_stream(self.socket.sendall)

    # Read a payload from the server connection stream
    def read_payload(self):
        return self.reader.read(self.socket.recv)

    def is_connected(self):
        return self.connection

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.connection = True
        except socket.timeout as st:
            print(st)

    def close_client(self):
        """ marks the socket closed """
        try:
            # print("self.kill_threads()")      # DEBUG
            # self._kill_threads()
            print("self.connection = False")  # DEBUG
            self.connection = False
            print("self.socket.close()")      # DEBUG
            self.socket.close()
            print("CLIENT DED")               # DEBUG
        except Exception as e:
            print(e)



if __name__ == "__main__":

    from fractal_reader import FractalReader
    from fractal_payload import Payload

    from fractal_segment import JsonSegment
    from fractal_segment import FileSegment

    HOST = 'localhost'    # The remote host
    PORT = 9876           # The same port as used by the server

    # CONNECT TO SERVER
    client = FractalClient(HOST, PORT, FractalReader())

    # CREATE PAYLOADS
    payload = Payload("gate_ping")

    # SEND PAYLOAD
    client.send_payload(payload)

    # RECEIVE PAYLOADS
    receivedPyloadisHere = client.read_payload()
    print("payload_name: ", receivedPyloadisHere.payload_name)
    print("payload_data: ", receivedPyloadisHere.payload_data)
    print("    segments: ", receivedPyloadisHere.segments)