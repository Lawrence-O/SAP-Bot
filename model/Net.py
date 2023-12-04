import torch
import torch.nn as nn
import pickle
import cv2
import os


class ONNX_NET():
    def __init__(self, data_path, onnx_path) -> None:
        self.data_path = data_path
        self.onnx_path = onnx_path
        
        self.data = None
        self.class_to_idx = None
        self.idx_to_class = None
        self.onnx_net = None

    def initialize(self):
        # with open(self.data_path, "rb") as handle:
        #     self.data = pickle.load(handle)
        # self.class_to_idx = self.data["class_to_idx"]
        # self.idx_to_class = self.data["idx_to_class"]
        self.onnx_net = cv2.dnn.readNetFromONNX(self.onnx_path)
        self.onnx_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.onnx_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
    def get_onnx_net(self):
        if not self.onnx_net:
            self.initialize()
        return self.onnx_net
