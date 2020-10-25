import numpy as np
import torch
import time
import cv2
import os
import sys


"""
    - utils.data
    - -------------| load_tensor
    - -------------| save_tensor
    - -------------| load_embeddings
    - -------------| save_embeddings
    - -------------| get_embeddings_from_bytes
    - -------------| get_bytes_from_embeddings
"""


def compare_embeddings(e1, e2):
    return (e1 - e2).norm().item()


def image_to_embedding(path_to_img, face_detecter, face_embedder):
    frame = cv2.imread(path_to_img)
    face = face_detecter.predict_faces(frame)
    x_min, y_min, x_max, y_max = face
    face_crop = frame[int(y_min): int(y_max), int(x_min): int(x_max)]
    face_embedding = face_embedder.frame_to_embedding(face_crop)
    return face_embedding


def create_embeddings_dict_from_images(path_to_images, face_detecter, face_embedder):
    face_embeddings = {}
    for image in os.listdir(path_to_images):
        filename = f'{path_to_images}/{image}'
        img_name = image.split(".")[0]
        img_emb = image_to_embedding(filename, face_detecter, face_embedder)
        face_embeddings[f"{img_name}"] = img_emb
    return face_embeddings


def load_embeddings_to_dict(path_to_embeddings):
    face_embeddings = {}
    for embedding_file in os.listdir(path_to_embeddings):
        full_path = f'{path_to_embeddings}/{embedding_file}'
        new_name = embedding_file.split(".")[0]
        face_embeddings[f"{new_name}"] = torch.load(full_path)
    print("Loaded: " + str(len(face_embeddings)) + " embeddings.")
    return face_embeddings


if __name__ == "__main__":
    pass

    # path = "../assets/images/xx_anchors"
    # print(load_embeddings_to_dict(path))
    # for embedding_file in os.listdir(path):
    #     file_path = f'{path}/{embedding_file}'
    #     name = file_path.split(path)[1]
    #     name = name.split("/")[1]
    #     name = name.split(".")[0]
    #     print(name)
