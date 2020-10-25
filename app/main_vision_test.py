# !/usr/bin/python3
# -*- coding: utf-8 -*-
from classes.face_embedder import FaceEmbedder
from classes.face_recognizer import FaceRecognizer
from classes.video_camera import VideoCamera
from classes.video_canvas import VideoCanvas
from utils.data import compare_embeddings, load_embeddings_to_dict
import numpy as np
import torch
import time
import cv2
import os

PATH_TO_FACE_DETECTION_MODEL = "./assets/models/RFB-640/face_model.pth"

if __name__ == "__main__":

    detector = FaceRecognizer(PATH_TO_FACE_DETECTION_MODEL)

    # TEST ON UR IMAGE
    INSERTED_FACE_IMAGE = "./assets/images/test_random/scotty.jpg"

    frame = cv2.imread(INSERTED_FACE_IMAGE)
    face_boxes = detector.predict_faces(frame)

    for box in face_boxes:
        print(f"FACE COORDS: {box}")
