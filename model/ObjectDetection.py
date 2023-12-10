import cv2
# import cv2.legacy as legacys
import numpy as np
import concurrent.futures


# from sensors import camera
from imutils.object_detection import non_max_suppression


# SAP_INPUT_IMAGE_SIZE = (128,128)
SAP_INPUT_IMAGE_SIZE = (224,224)
YOLO_INPUT_IMAGE_SIZE = (640,640)
# SAP_ONNX_DATA_PATH = "./bin/sap_yolo_data.pickle"
SAP_ONNX_MODEL_PATH = "./bin/yolov8_sap.onnx"
# ORG_ONNX_DATA_PATH = "./bin/org_yolo_data.pickle"
ORG_ONNX_MODEL_PATH = "./bin/yolov8s.onnx"
MINIMUM_DETECTION_SCORE = 0.3
MINIMUM_CLASS_SCORE = 0.6
# SAP_DETECTION_WEIGHT = 0.6
CLASS_ID_SAP_OFFSET = 80
SAP_CLASS_LABEL_IGNORES = [85]
YOLO_CLASS_LABEL_IGNORES = [33]
PENALTY_CLASS_LABELS = [0]

class ObjectDetector():
    def __init__(self):
        self.yolo_sap = cv2.dnn.readNetFromONNX(SAP_ONNX_MODEL_PATH)
        self.yolo_org = cv2.dnn.readNetFromONNX(ORG_ONNX_MODEL_PATH)
        # self.tracker = legacy.TrackerMOSSE().create()
    def preprocess_frame(self,frame,resize_size):
        print(frame.shape)
        print(resize_size)
        return cv2.dnn.blobFromImage(frame, 1/255.0,size=resize_size,swapRB=True,crop=False)
    def process_frame(self,blob,model):
        net = model
        net.setInput(blob)
        predictions = net.forward()
        return  predictions.transpose((0, 2, 1))
    def unwrap_detections(self, frame, cnn_output, resize_size, class_id_offset=0, ignore_label=None):
        labels = dict()
        image_height, image_width, _ = frame.shape
        x_factor = image_width / resize_size[0]
        y_factor = image_height / resize_size[1]
       
        positions = cnn_output[0][:, :4]
        confidences = cnn_output[0][:, 4]
        classes_scores = cnn_output[0][:, 4:]

        # Find the index of the class with maximum score
        max_class_indices = np.argmax(classes_scores, axis=1)
        max_class_scores = np.max(classes_scores, axis=1)
        
        # Apply filtering conditions
        valid_indices = max_class_scores > MINIMUM_CLASS_SCORE
        valid_labels = max_class_indices + class_id_offset

        # Check for ignore_label
        if ignore_label is not None:
            ignore_mask = np.isin(valid_labels, ignore_label)
            valid_indices &= ~ignore_mask  # Exclude ignored labels

        # Extract valid data using boolean indexing
        valid_positions = positions[valid_indices]
        valid_confidences = confidences[valid_indices]
        valid_class_indicies = max_class_indices[valid_indices] + class_id_offset

        if not valid_positions.all():
            return labels  # No valid positions after filtering

        # Calculate bounding boxes
        left = ((valid_positions[:, 0] - 0.5 * valid_positions[:, 2]) * x_factor).astype(int)
        top = ((valid_positions[:, 1] - 0.5 * valid_positions[:, 3]) * y_factor).astype(int)
        width = (valid_positions[:, 2] * x_factor).astype(int)
        height = (valid_positions[:, 3] * y_factor).astype(int)

        boxes = np.column_stack([left, top, width, height])

        # Extract class_id using class_id_offset
        class_ids = valid_class_indicies + class_id_offset

        # Corrected class_id extraction
        labels = {class_id: [] for class_id in class_ids}

        # Populate the labels dictionary
        for i, class_id in enumerate(class_ids):
            box = boxes[i]
            conf = valid_confidences[i]
            labels[class_id].append((box, conf))
        # print("PRE POPULATED LABELS DICT",labels)
        return labels
    def apply_nms(self, detections):
        #Concatinate Matrixes to only 1 (each row is an object)
        final_detections = dict()
        for label in detections:
            bboxes = np.array([b[0] for b in detections[label]])
            probs = np.array([p[1] for p in detections[label]])
            converted_boxes = np.column_stack([
            bboxes[:, 0], bboxes[:, 1],
            bboxes[:, 0] + bboxes[:, 2], bboxes[:, 1] + bboxes[:, 3]
        ])
            boxes = non_max_suppression(np.array(converted_boxes),probs,overlapThresh=0.8)
            final_detections[label] = boxes
        return final_detections
    def get_detections(self, frame, input_size, model, class_id_offset, ignore_label):
        blob = self.preprocess_frame(frame, input_size)
        output = self.process_frame(blob, model=model)
        return self.unwrap_detections(frame, output, input_size, class_id_offset, ignore_label=ignore_label)
    def get_pest_detections(self, frame):
        return self.get_detections(frame, SAP_INPUT_IMAGE_SIZE, self.yolo_sap, CLASS_ID_SAP_OFFSET, ignore_label=SAP_CLASS_LABEL_IGNORES)
    def get_object_detections(self, frame):
        return self.get_detections(frame, YOLO_INPUT_IMAGE_SIZE, self.yolo_org, 0, ignore_label=YOLO_CLASS_LABEL_IGNORES)
    def get_combined_detections(self, frame):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            pest_detections_future = executor.submit(self.get_pest_detections, frame)
            object_detections_future = executor.submit(self.get_object_detections, frame)
            pest_detections = pest_detections_future.result()
            object_detections = object_detections_future.result()
        return self.apply_nms(pest_detections | object_detections)
    def get_bbox_centroid(self,bbox):
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        return np.array([cx, cy])
    def find_object_scores(self,objects_bboxes,penalty_bboxes,camera_position,image_size):
        object_positions = np.array([self.get_bbox_centroid(bbox) for bbox in objects_bboxes])
        camera_distances = np.linalg.norm(object_positions - camera_position, axis=1)
        penalties = np.zeros(len(objects_bboxes))
        scores = (1.0 / (camera_distances))
        if penalty_bboxes:
            penalty_positions = np.array([self.get_bbox_centroid(bbox) for bbox in penalty_bboxes])
            distances_to_penalties = np.linalg.norm(object_positions[:, np.newaxis, :] - penalty_positions, axis=2)
            penalties = 1.1 / (distances_to_penalties)
            scores -= penalties.sum(axis=1)  
        # Compute the scores based on the inverse square distance to the camera and penalties
        return objects_bboxes,scores
    def get_target_scores(self,frame):
        detections = self.get_combined_detections(frame)
        object_bboxes = []
        penalty_bboxes = []
        for label, bboxes_list in detections.items():
            for bbox in bboxes_list:
                if label >= CLASS_ID_SAP_OFFSET:
                    object_bboxes.append(bbox)
                elif label in PENALTY_CLASS_LABELS:
                    penalty_bboxes.append(bbox)
        camera_y,camera_x = frame.shape[0] // 2, frame.shape[1] // 2
        targets,scores = self.find_object_scores(object_bboxes,penalty_bboxes,(camera_x,camera_y),frame.shape)
        return targets,scores
    
    