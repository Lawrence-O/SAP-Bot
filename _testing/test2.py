from model import ConvNet
import cv2
import numpy as np
import random

from imutils.object_detection import non_max_suppression

img_path = "./testimg3.jpg"
# load the input image
image = cv2.imread(img_path)
image = cv2.resize(image, (1024,1024))
model_path = "./bin/data_final_7.pickle"
onnx_net = ConvNet.ONNX_NET(model_data_path=model_path)
opencv_net = onnx_net.get_onnx_net()

def selective_search(image, method="fast"):
	# initialize OpenCV's selective search implementation and set the
	# input image
	ss = cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()
	ss.setBaseImage(image)
	# check to see if we are using the *fast* but *less accurate* version
	# of selective search
	if method == "fast":
		ss.switchToSelectiveSearchFast()
	# otherwise we are using the *slower* but *more accurate* version
	else:
		ss.switchToSelectiveSearchQuality()
	# run selective search on the input image
	rects = ss.process()
	# return the region proposal bounding boxes
	return rects

H,W = 1024,1024
rects = selective_search(image)

# initialize the list of region proposals that we'll be classifying
# along with their associated bounding boxes
proposals = []
boxes = []

# loop over the region proposal bounding box coordinates generated by
# running selective search
for (x, y, w, h) in rects:
    # if the width or height of the region is less than 10% of the
    # image width or height, ignore it (i.e., filter out small
    # objects that are likely false-positives)
    if w / float(W) < 0.1 or h / float(H) < 0.1:
        continue
    # extract the region from the input image, convert it from BGR to
    # RGB channel ordering, and then resize it to 224x224 (the input
    # dimensions required by our pre-trained CNN)
    roi = image[y:y + h, x:x + w]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    roi = cv2.resize(roi, (64, 64))
    # update our proposals and bounding boxes lists
    proposals.append(roi)
    boxes.append((x, y, w, h))

proposals = np.array(proposals)
labels = dict()

for i,region in enumerate(proposals):
    mean = np.array([0.485, 0.456, 0.406]) * 255.0
    scale = 1 / 255.0
    std = [0.229, 0.224, 0.225]
    input_blob = cv2.dnn.blobFromImage(
        image=region,
        scalefactor=scale,
        size=(64, 64),  # img target size
        mean=mean,
        swapRB=True,  # BGR -> RGB
        crop=False  # center crop
        )
    input_blob[0] /= np.asarray(std, dtype=np.float32).reshape(3, 1, 1)
    opencv_net.setInput(input_blob)
    output = opencv_net.forward()
    print("OpenCV DNN prediction: \n")
    print("* shape: ", output.shape)
    class_id = np.argmax(output)
    confidence = output[0][class_id]
    label = onnx_net.idx_to_class[class_id]
    print("* class ID: {}, label: {}".format(class_id,label))
    print("* confidence: {:.4f}".format(confidence))
    if confidence >= 33:
        (x, y, w, h) = boxes[i]
        box = (x, y, x + w, y + h)
        L = labels.get(label, [])
        L.append((box, confidence))
        labels[label] = L

# loop over the labels for each of detected objects in the image
for label in labels.keys():
	# clone the original image so that we can draw on it
	print("[INFO] showing results for '{}'".format(label))
	clone = image.copy()
	# loop over all bounding boxes for the current label
	for (box, prob) in labels[label]:
		# draw the bounding box on the image
		(startX, startY, endX, endY) = box
		cv2.rectangle(clone, (startX, startY), (endX, endY),
			(0, 255, 0), 2)
	# show the results *before* applying non-maxima suppression, then
	# clone the image again so we can display the results *after*
	# applying non-maxima suppression
	cv2.imshow("Before", clone)
	clone = image.copy()
	# extract the bounding boxes and associated prediction
	# probabilities, then apply non-maxima suppression
	boxes = np.array([p[0] for p in labels[label]])
	proba = np.array([p[1] for p in labels[label]])
	boxes = non_max_suppression(boxes, proba)
	# loop over all bounding boxes that were kept after applying
	# non-maxima suppression
	for (startX, startY, endX, endY) in boxes:
		# draw the bounding box and label on the image
		cv2.rectangle(clone, (startX, startY), (endX, endY),
			(0, 255, 0), 2)
		y = startY - 10 if startY - 10 > 10 else startY + 10
		cv2.putText(clone, label, (startX, y),
			cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
	# show the output after apply non-maxima suppression
	cv2.imshow("After", clone)
	cv2.waitKey(0)