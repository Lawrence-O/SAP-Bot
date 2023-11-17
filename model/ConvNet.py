import torch
import torch.nn as nn
import pickle

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

class OONX_NET():
    def __init__(self, model_data_path) -> None:
        self.data_path = model_data_path
        self.data = None
        self.model_weights = None
        self.class_to_idx = None
        self.idx_to_class = None
        self.num_classes = None


        self.oonx_net = None

    def initialize_data(self):
        with open(self.data_path, "rb") as handle:
            self.data = pickle.load(handle)
        self.model_weights = self.data["model"]
        self.class_to_idx = self.data["class_to_idx"]
        self.idx_to_class = self.data["idx_to_class"]
        self.num_classes = len(self.class_to_idx.keys())
    def initialize_oonx_net(self):
        if not self.pytorch_model:
            self.initialize_data()
        if not self.model_architecture:
            net = ConvNet(num_classes=self.num_classes)
            
    def get_oonx_net(self):

        

