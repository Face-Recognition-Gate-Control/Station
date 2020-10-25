import numpy as np
import cv2


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


    def test(self):
        print("ok")

# TESTING
if __name__ == "__main__":
    pass
