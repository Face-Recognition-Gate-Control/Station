import socket
import threading


HOST = "localhost"    # The remote host
PORT = 1337           # The same port as used by the server

class TestClient(threading.Thread):

    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
        self.terminate = False
        self.content = "ERROR CONTENT"
        self.command = " ERROR COMMAND"
        self.trigger = False


    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            print("Connected: ", self.is_connected)
        except socket.error as err:
            print("Connect() failed: ", err)

    def on_trigger(self, msg):
        self.command = msg
        self.trigger = True

    def run(self):
        self.connect()
        while not self.terminate:
            if self.trigger:
                self.send_response(self.command)
                self.content = self.read_response()
                self.trigger = False

                if self.command == "exit":
                    self.close()

    def close(self):
        print("Closed client!")
        self.is_connected = False
        self.terminate = True
        self.socket.close()
        self.join()


    def send_response(self, msg: str):
        self.socket.sendall(msg.encode("UTF-8"))
        print("SEND: " + msg)

    def read_response(self):
        msg = self.socket.recv(1024).decode("UTF-8")
        print(" GOT: " + msg)
        return msg

if __name__ == "__main__":

    client = LocalClient(HOST, PORT)

    try:
        client.start()
    except:
        client.close()



