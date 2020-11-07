# !/usr/bin/python3
# -*- coding: utf-8 -*-
# from src import *
# from app.detection.face_recognizer import FaceRecognizer
from core.detection.face_recognizer import FaceRecognizer
import cv2

PATH_TO_FACE_DETECTION_MODEL = "./static/models/RFB-640/face_model.pth"

if __name__ == "__main__":
    
    detector = FaceRecognizer(PATH_TO_FACE_DETECTION_MODEL)

    # TEST ON UR IMAGE
    INSERTED_FACE_IMAGE = "./static/images/test_random/scotty.jpg"

    frame = cv2.imread(INSERTED_FACE_IMAGE)
    face_boxes = detector.predict_faces(frame)

    for box in face_boxes:
        print(f"FACE COORDS: {box}")
