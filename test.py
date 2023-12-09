from ultralytics import YOLO


print("starting")
model = YOLO("./bin/best.pt")
model.export(format="ONNX",simplify=True,opset=12)
print("done")