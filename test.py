from ultralytics import YOLO


print("starting")
model = YOLO("./bin/best.pt")
model.export(format="ONNX",simplify=True)
print("done")