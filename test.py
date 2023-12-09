from ultralytics import YOLO


print("starting")
model = YOLO("./bin/yolov8_org.pt")
model.export(format="ONNX",simplify=True,opset=12,dynamic=False)
print("done")