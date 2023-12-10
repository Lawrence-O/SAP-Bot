# import cv2.legacy as legacy
import numpy as np

class ObjectTracker():
    def __init__(self):
        # self.tracker = legacy.TrackerMOSSE().create()
        pass
    def gaussian(self,x,a=1):
        return np.exp(-a*x**2)
    
    # def get_new_object_position(self,old_frame,new_frame,bbox):
    #     self.tracker.init(old_frame,bbox)
    #     (success, new_bbox) = self.tracker.update(new_frame)
    #     return new_bbox if success else None