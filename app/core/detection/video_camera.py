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

    def get_roi(self, crop):
        """creates a crop based upon the original size of the frame
        from the video capturing device

        Args:
            crop ([tuple/list]): [the required min/max positions]

        Returns:
            [numpy.ndarray]: [reduced size of the frame]
        """
        x_min, y_min, x_max, y_max = crop
        return self.main_frame[int(y_min):int(y_max), int(x_min):int(x_max)]

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

# TESTING
if __name__ == "__main__":

    cap = cv2.VideoCapture(1)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        cv2.imshow('frame',gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

