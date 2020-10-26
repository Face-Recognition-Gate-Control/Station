# !/usr/bin/python3
# -*- coding: utf-8 -*-
from core.detection.face_embedder import FaceEmbedder
from core.detection.face_recognizer import FaceRecognizer
from core.detection.video_camera import VideoCamera
from core.detection.video_canvas import VideoCanvas
from core.utils.data import compare_embeddings, load_embeddings_to_dict
import numpy as np
import torch
import time
import cv2
import os

# TODO: (Idea) Create Configloader?
# TODO: (Idea) Create Dataloader?

# TODO: Where to place this?
PATH_TO_FACE_DETECTION_MODEL = "./static/models/RFB-640/face_model.pth"

# TODO: Where to place this?
# TODO: import local weigths into Embedd-model (be careful inside ML-modules)
PATH_TO_FACE_EMBEDDING_MODEL = "./static/models/InceptionResnetV1/vggface2.pth"

# TODO: Where to place this?
PATH_TO_ANCHORS = "static/images/test_embeddings"
PATH_TO_IMAGES = "static/images/test_images"
PATH_TO_CROPS = "static/images/test_crops"

if __name__ == "__main__":

    camera = VideoCamera(SRC=1)
    canvas = VideoCanvas()
    face_embedder = FaceEmbedder()
    face_detector = FaceRecognizer(PATH_TO_FACE_DETECTION_MODEL)

    # " DATABASE "
    embeddings = load_embeddings_to_dict(PATH_TO_ANCHORS)

    start_time = time.time()
    WAIT_TIME = 2
    guesses = 0
    predicted_name = ""
    predicted_dist = ""

    while True:

        current_time = time.time() - start_time
        frame = camera.get_frame()
        face_boxes = face_detector.predict_faces(frame)

        for face_box in face_boxes:
            canvas.draw_rectangle(frame, face_box)

            if current_time > WAIT_TIME:

                face_crop = camera.get_roi(face_box)
                face_emb = face_embedder.frame_to_embedding(face_crop)

                # TODO: do better
                lowest_name = ""
                lowest_dist = 10  # random number greater then ie. 1.5

                for db_name, db_emb in embeddings.items():
                    dist = compare_embeddings(face_emb, db_emb)
                    if dist < lowest_dist:
                        lowest_dist = dist
                        lowest_name = db_name

                predicted_name = lowest_name
                predicted_dist = round(lowest_dist, 3)
                guesses += 1
                start_time = time.time()

        canvas.draw_text(frame, (20, 40),  f"guesses   : {guesses}")
        canvas.draw_text(frame, (20, 85),  f"pred dist : {predicted_dist}")
        canvas.draw_text(frame, (20, 130), f"pred name : {predicted_name}")
        canvas.display_frame(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
