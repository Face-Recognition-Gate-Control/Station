import cv2
# TODO: Move to somewhere smart?
WINDOW_TITLE = "FACIAL RECOGNITION SOFTWARE"
TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX
GRN_COLOR = (0, 255, 0)  #   GREEN = VALID
RED_COLOR = (0, 0, 255)  # RED = NON VALID

LINE_THICKNESS = 2       # px
TEXT_SCALE = 1           # px
PADDING = 30             # px

class VideoCamera():
    def __init__(self):
        self.camera = cv2.VideoCapture(1)

    def __del__(self):
        self.camera.release()

    def read_frame(self):
        _, frame = self.camera.read()
        return frame

    def get_frame(self):
        temp = self.read_frame()
        _, frame_buffer = cv2.imencode('.jpg', temp)
        return frame_buffer.tobytes()

    def frame_to_bytes(self, frame):
        _, frame_buffer = cv2.imencode('.jpg', frame)
        return frame_buffer.tobytes()

    def save_frame(self, frame, name):
        cv2.imwrite(name, frame)

    def draw_rect(self, rect):
        ret, frame = self.camera.read()
        ret, frame_buffer = cv2.imencode('.jpg', frame)
        return frame_buffer.tobytes()



    @staticmethod
    def draw_rectangle(frame, coords):
        """Used to display an rectangle onto the a given frame to the window.
        Args:
            frame ([numpy.ndarray]): [the frame to draw the rectangle onto]
            coords ([list]): [list of min/max set points]
        """
        return cv2.rectangle(frame, (int(coords[0]), int(coords[1])),  (int(coords[2]), int(coords[3])),
                      VideoCamera.get_color(coords), LINE_THICKNESS)

    @staticmethod
    def valid_size(coords):
        """ format: xmin, ymin, xmax, ymax """
        WIDTH_REQUIRED  = 130
        HEIGTH_REQUIRED = 190
        WIDTH_TEST = coords[2] - coords[0]
        HEIGTH_TEST = coords[3] - coords[1]
        if (WIDTH_TEST > WIDTH_REQUIRED):
            if(HEIGTH_TEST > HEIGTH_REQUIRED):
                return True
        return False

    @staticmethod
    def get_color(frame):
        if VideoCamera.valid_size(frame):
            return GRN_COLOR
        return RED_COLOR




if __name__ == "__main__":

    cam = VideoCamera()
    # while True:
    #     # Capture frame-by-frame
    #     frame = cam.get_frame()
    #     cv2.imshow('Webcam', frame)
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    # cv2.destroyAllWindows()


    SHOW_FACE_BOX = True
    face_embedder = None
    face_detector = None
    VALIDATE_FACE = True
    TIMER_EXPIRED = 1 # Seconds
    #TODO Smart loop-timer (0.5 seconds)

    # Below stuff wont work, so chill
    while True:

        frame = cam.read_frame()
        # face_boxes = face_detector.predict_faces(frame)

        # for face_box in face_boxes:
        #     if VALIDATE_FACE:
        #         if VideoCamera.valid_size(face_box):
        #             counter.start()
        #             if counter.is_expired():
        #                 face = cam.get_roi(face_box)
        #                 cv2.imwrite("./tmp/face.jpg", face)
        #                 # embedding = face_embedder.frame_to_embedding(face)
        #                 # disp_que.add_response({
        #                 #     "response_name": "user_authorization",
        #                 #     "embedding": embedding
        #                 # })
        #                 # start_confirmation_timer_from_server()
        #         else:
        #             counter.stop()

        #     if SHOW_FACE_BOX:
        #         frame = VideoCamera.draw_rectangle(frame, face_box)
        cv2.imshow("WINDOW", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break