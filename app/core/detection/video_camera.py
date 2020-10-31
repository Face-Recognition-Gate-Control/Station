import numpy as np
import cv2

WINDOW_TITLE = "FACIAL RECOGNITION SOFTWARE"
TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX
GRN_COLOR = (0, 255, 0)  #   GREEN = VALID
RED_COLOR = (0, 0, 255)  # RED = NON VALID

LINE_THICKNESS = 2       # px
TEXT_SCALE = 1           # px
PADDING = 30             # px

class VideoCamera():
    """
    This class is tailored to access and return the video captures devices frames
    """

    def __init__(self, SRC=0, WINDOW_WIDTH=640, WINDOW_HEIGHT=480):
        """Generates an instance of the video camera,
        used to access the given video caputring device,
        defaulted to cv2 standards

        Args:
            SRC (int, optional): [the source / port of your web-camera]. Defaults to 0 of USB_cams
            WINDOW_WIDTH (int, optional): [default cv2-size]. Defaults to 640.
            WINDOW_HEIGHT (int, optional): [default cv2-size]. Defaults to 480.
        """
        self.cap = cv2.VideoCapture(SRC)
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.is_interrupted = False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.WINDOW_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.WINDOW_HEIGHT)

    def __del__(self):
        """
        Detaches the object from the creates video-capturing device
        """
        print("Closing camera!")
        self.cap.release()

    def get_frame(self):
        """captures the frame of the video-capturing devices, and returns it

        Returns:
            [numpy.ndarray]: [ndarray representing the frame]
        """
        _, self.main_frame = self.cap.read()
        return self.main_frame

    @staticmethod
    def crop_frame(frame, crop):
        """creates a crop based upon the original size of the frame
        from the video capturing device

        Args:
            crop ([tuple/list]): [the required min/max positions]

        Returns:
            [numpy.ndarray]: [reduced size of the frame]
        """
        x_min, y_min, x_max, y_max = crop
        return frame[int(y_min):int(y_max), int(x_min):int(x_max)]
    
    @staticmethod
    def frame_to_bytes(frame):
        """ converts a numpy.ndarray into bytes

        Args:
            frame ([numpy.ndarray]): frame

        Returns:
            [bytes]: [output buffer]
        """
        _, frame_buffer = cv2.imencode('.jpg', frame)
        return frame_buffer.tobytes()

    @staticmethod
    def save_thumbnail(frame, face_box, name):
        """saves an face image with a given padding added_layer

        Args:
            frame (numpy.ndarray): frame
            face_box (numpy.ndarray): face COORDS
            name (filename): name of file
        """
        save_directory = f"static/images/tmp/{name}.jpg"
        x_min, y_min, x_max, y_max = face_box
        H_PAD = 20
        W_PAD = 40
        face_thumbnail = frame[int(y_min-H_PAD):int(y_max+H_PAD), int(x_min-W_PAD):int(x_max+W_PAD)]
        cv2.imwrite(save_directory, face_thumbnail)

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
        """checks if coords size is valid

        Args:
            coords (numpy.ndarray): coords
            'format: xmin, ymin, xmax, ymax'

        Returns:
            bool: true if valid size, false otherwise
        """
        WIDTH_REQUIRED  = 150
        HEIGTH_REQUIRED = 250
        WIDTH_TEST = coords[2] - coords[0]
        HEIGTH_TEST = coords[3] - coords[1]

        if (WIDTH_TEST > WIDTH_REQUIRED):
            if(HEIGTH_TEST > HEIGTH_REQUIRED):
                return True
        return False

    @staticmethod
    def get_color(frame):
        """ returns valid (green) color, red otherwise

        Args:
            frame (numpy.ndarray): frame

        Returns:
            tuple: RGB colors
        """
        if VideoCamera.valid_size(frame):
            return GRN_COLOR
        return RED_COLOR

if __name__ == "__main__":

    cap = VideoCamera()

    while True:

        frame = cap.get_frame()

        cv2.imshow('Window', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

