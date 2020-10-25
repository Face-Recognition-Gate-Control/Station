import socket
import time


HOST = "localhost"    # The remote host
PORT = 1337         # The same port as used by the server

class LocalClient():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
        self.client_id = "Client_X"

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            print("Connected: ", self.is_connected)
        except socket.error as err:
            print("Connect() failed: ", err)

    def close(self):
        print("Closed client!")
        self.is_connected = False
        self.socket.close()

    def send_response(self, msg: str):
        self.socket.sendall(msg.encode("UTF-8"))
        print("Sent: " + msg)

    def read_response(self):
        # HEADER_LENGTH = 125
        # BODY_LENGTH = 42
        # DATA_SIZE = HEADER_LENGTH + BODY_LENGTH
        # data = ""
        curr = self.socket.recv(1024).decode()
        print("Recv: " + curr)
        #if len(curr) < 1:
        return curr

    def run_stuff(self):
        while self.is_connected:
            try:
                self.send_response()
                self.read_response()
        except:
            self.close()



if __name__ == "__main__":

    client = LocalClient(HOST, PORT)
    client.connect()


    now = time.time()
    try:
        while True:
            time.sleep(1)
            curr_time = time.time()
            elapsed = curr_time-now
            client.send_response(str(elapsed))
            resp = client.read_response()
            print(resp)

            if elapsed > 10:
                GGS = "STOP"
                client.send_response(GGS)
                break
    except Exception as e:
        print(e.with_traceback())
    finally:
        client.close()



    # STUFF = "GET / HTTP/1.1\r\nHost:%s\r\n\r\n" % HOST
    # #STUFFX = "GET / HTTP/1.1\r\nHost: %s\r\nAccept: application/json\r\nConnection: close\r\n\r\n" % HOST

    # cmds = ["1", "2", "3", "STOP"]




