# FRACTAL
from utils.msg_queues.response_dispatcher import ResponseDispatcher
from utils.msg_queues.response_receiver import ResponseReceiver
from utils.socket.fractal_client import FractalClient
from utils.socket.fractal_reader import FractalReader
from utils.debug_tools.timer import Timer
import queue

REMOTE_HOST = "localhost"
REMOTE_PORT = 9876
recv_que = ResponseReceiver()
disp_que = ResponseDispatcher()
client = FractalClient(REMOTE_HOST, REMOTE_PORT, FractalReader())
client.set_queues(disp_que, recv_que)

if __name__ == "__main__":

    client.init() # START

    debug_t1 = Timer(2)
    debug_t2 = Timer(4)
    debug_t1.start()
    debug_t2.start()

    while True:
        
        if debug_t2.is_expired():
            debug_t2.stop()
            break

        if debug_t1.is_expired():
            debug_t1.stop()
            disp_que.add_response({"response_name": "gate_ping"})

        try:
            msg = recv_que.get_response()
            recv_que.confirm_sent()
        except queue.Empty:
            pass


    client.close_client()
    debug_t1.stop()
    debug_t2.stop()
    print("Done!")


    # # CREATE PAYLOADS
    # payload = Payload("gate_ping")

    # # SEND PAYLOAD
    # client.send_payload(payload)

    # # RECEIVE PAYLOADS
    # receivedPyloadisHere = client.read_payload()
    # print("payload_name: ", receivedPyloadisHere.payload_name)
    # print("payload_data: ", receivedPyloadisHere.payload_data)
    # print("    segments: ", receivedPyloadisHere.segments)