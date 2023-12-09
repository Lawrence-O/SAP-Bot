from ultralytics import YOLO


print("starting")
model = YOLO("yolov8s.pt")
model.export(format="ONNX",simplify=True,opset=12,dynamic=False)
print("done")