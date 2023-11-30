from model import ConvNet
import cv2
import numpy as np



model_path = "./bin/data_final_7.pickle"
onnx_net = ConvNet.ONNX_NET(model_data_path=model_path)
opencv_net = onnx_net.get_onnx_net()

img_path = "./2.jpg"
# read the image
input_img = cv2.imread(img_path, cv2.IMREAD_COLOR)
input_img = input_img.astype(np.float32)

# target image sizes
img_height = input_img.shape[0]
img_width = input_img.shape[1]

# define preprocess parameters
mean = np.array([0.485, 0.456, 0.406]) * 255.0
scale = 1 / 255.0
std = [0.229, 0.224, 0.225]
# prepare input blob to fit the model input:
# 1. subtract mean
# 2. scale to set pixel values from 0 to 1
input_blob = cv2.dnn.blobFromImage(
    image=input_img,
    scalefactor=scale,
    size=(64, 64),  # img target size
    mean=mean,
    swapRB=True,  # BGR -> RGB
    crop=False  # center crop
)
# 3. divide by std
input_blob[0] /= np.asarray(std, dtype=np.float32).reshape(3, 1, 1)

COLORS = np.random.uniform(0, 255, size=(21, 3))
# set OpenCV DNN input
opencv_net.setInput(input_blob)
# OpenCV DNN inference
detections = opencv_net.forward()

# # loop over the detections
# for i in np.arange(0, detections.shape[2]):
# 	# extract the confidence (i.e., probability) associated with the
# 	# prediction
# 	confidence = detections[0, 0, i, 2]
# 	# filter out weak detections by ensuring the `confidence` is
# 	# greater than the minimum confidence
# 	if confidence > 10:
# 		# extract the index of the class label from the `detections`,
# 		# then compute the (x, y)-coordinates of the bounding box for
# 		# the object
# 		idx = int(detections[0, 0, i, 1])
# 		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
# 		(startX, startY, endX, endY) = box.astype("int")
# 		# display the prediction
# 		label = "{}: {:.2f}%".format(onnx_net.idx_to_class[idx], confidence * 100)
# 		print("[INFO] {}".format(label))
# 		cv2.rectangle(input_img, (startX, startY), (endX, endY),
# 			COLORS[idx], 2)
# 		y = startY - 15 if startY - 15 > 15 else startY + 15
# 		cv2.putText(input_img, label, (startX, y),
# 			cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

# print("OpenCV DNN prediction: \n")
# print("* shape: ", out.shape)
# # get the predicted class ID
# print(out)
# imagenet_class_id = np.argmax(out)
# # get confidence
# confidence = out[0][imagenet_class_id]
# print("* class ID: {}, label: {}".format(imagenet_class_id, onnx_net.idx_to_class[imagenet_class_id]))
# print("* confidence: {:.4f}".format(confidence))