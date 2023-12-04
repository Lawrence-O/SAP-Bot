import cv2.legacy as legacy
import numpy as np

class ObjectTracker():
    def __init__(self):
        self.tracker = legacy.TrackerMOSSE().create()
    def gaussian(self,x,a=1):
        return np.exp(-a*x**2)
    def get_bbox_centroid(self,bbox):
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        return np.array([cx, cy])
    def find_object_scores(self,objects_bboxes,penalty_bboxes,camera_position):
        object_positions = np.array([self.get_bbox_centroid(bbox) for bbox in objects_bboxes])
        print("object pos",object_positions)
        camera_distances = np.linalg.norm(object_positions - camera_position, axis=1)
        print("camera distance", camera_distances,camera_position)
        penalties = np.zeros(len(objects_bboxes))
        if penalty_bboxes:
            penalty_positions = np.array([self.get_bbox_centroid(bbox) for bbox in penalty_bboxes])
            distances_to_humans = np.linalg.norm(object_positions[:, np.newaxis, :] - penalty_positions, axis=2)
            print("dst_humans",distances_to_humans)
            penalties = 1.0 / distances_to_humans
        # Compute the scores based on the inverse square distance to the camera and penalties
        print("penalties",penalties)
        scores = (1.0 / (camera_distances)) - penalties.sum(axis=1)
        return objects_bboxes,scores
    def get_new_object_position(self,old_frame,new_frame,bbox):
        self.tracker.init(old_frame,bbox)
        (success, new_bbox) = self.tracker.update(new_frame)
        return new_bbox if success else None