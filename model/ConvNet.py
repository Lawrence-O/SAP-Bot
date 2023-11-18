import torch
import torch.nn as nn
import pickle
import cv2

ONNX_NET_OUTPUT = "./bin/ConvNet.onnx"

class ConvNet(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.backbone = torch.nn.Sequential(
 
            torch.nn.Conv2d(in_channels=3, out_channels=64, kernel_size=7, stride=4, padding=3),
            torch.nn.BatchNorm2d(num_features=64),
            torch.nn.ReLU(),
            torch.nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=2, padding=1),
            torch.nn.BatchNorm2d(num_features=128),
            torch.nn.ReLU(),
            torch.nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, stride=2, padding=1),
            torch.nn.BatchNorm2d(num_features=256),
            torch.nn.ReLU(),
            torch.nn.Conv2d(in_channels=256, out_channels=512, kernel_size=3, stride=2, padding=1),
            torch.nn.BatchNorm2d(num_features=512),
            torch.nn.ReLU(),
            torch.nn.Conv2d(in_channels=512, out_channels=1024, kernel_size=3, stride=2, padding=1),
            torch.nn.BatchNorm2d(num_features=1024),
            torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d(output_size=1),
            torch.nn.Flatten()
        )

        self.cls_layer = torch.nn.Linear(1024,num_classes)

    def forward(self,x):
        x = self.backbone(x)
        x = self.cls_layer(x)
        return x

class ONNX_NET():
    def __init__(self, model_data_path) -> None:
        self.data_path = model_data_path
        self.data = None

        self.model_weights = None
        self.class_to_idx = None
        self.idx_to_class = None
        self.num_classes = None

        self.pytorch_net = None
        self.onnx_net = None

    def initialize_data(self):
        with open(self.data_path, "rb") as handle:
            self.data = pickle.load(handle)
        self.model_weights = self.data["model"]
        self.class_to_idx = self.data["class_to_idx"]
        self.idx_to_class = self.data["idx_to_class"]
        self.num_classes = len(self.class_to_idx)
    def initialize_onnx_net(self):
        if not self.data:
            self.initialize_data()
        if not self.pytorch_net:
            net = ConvNet(num_classes=self.num_classes)
            net.load_state_dict(self.model_weights)
            net.eval()
            self.pytorch_net = net
        torch.onnx.export(
            self.pytorch_net,
            torch.randn(1, 3, 64, 64, requires_grad=True),  
            ONNX_NET_OUTPUT,
            export_params=True,
            do_constant_folding=True,
            input_names = ['input'],
            output_names = ['output'],
            dynamic_axes={'input' : {0 : 'batch_size'},   
                                'output' : {0 : 'batch_size'}}
            )
    def get_onnx_net(self):
        if not self.onnx_net:
            self.initialize_onnx_net()
            self.onnx_net = cv2.dnn.readNetFromONNX(ONNX_NET_OUTPUT)
        return self.onnx_net
