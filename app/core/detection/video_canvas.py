import cv2


# TODO: Move to somewhere smart?
WINDOW_TITLE = "FACIAL RECOGNITION SOFTWARE"
TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX
BOX_COLOR = (0, 255, 0)  # BGR
LINE_THICKNESS = 2       # px
TEXT_SCALE = 1           # px
PADDING = 30             # px


class VideoCanvas():
    """
    This class is tailored to represent a wrapper for the a graphical window display,
    aswell as a canvas to show inserted text, numbers etc..
    """

    def __init__(self):
        pass

    def __del__(self):
        """
        Detaches and destroys the created GUI-window
        """
        print("Closing canvas!")
        cv2.destroyAllWindows()

    @staticmethod
    def display_frame(frame):
        """Used to display an image in a window.
        The window automatically fits to the image size.

        Args:
            frame ([numpy.ndarray]): [It is the image that is to be displayed.]
        """
        cv2.imshow(WINDOW_TITLE, frame)

    @staticmethod
    def draw_rectangle(frame, coords):
        """Used to display an rectangle onto the a given frame to the window.

        Args:
            frame ([numpy.ndarray]): [the frame to draw the rectangle onto]
            coords ([list]): [list of min/max set points]
        """
        return cv2.rectangle(frame, (int(coords[0]), int(coords[1])),  (int(coords[2]), int(coords[3])),
                      BOX_COLOR, LINE_THICKNESS)

    @staticmethod
    def draw_text(frame, coords, text):
        """Used to display a text onto the a given frame to the window.

        Args:
            frame ([numpy.ndarray]): [the frame to draw the rectangle onto]
            coords ([list]): [list of min/max set points]
            text ([str]): [the text to display]
        """
        if not isinstance(text, str):
            text = str(text)
        return cv2.putText(frame, text, (coords[0], coords[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (100, 100, 255), 2)

        # TESTING
if __name__ == "__main__":
    pass
