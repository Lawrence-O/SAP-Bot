from heapq import heapify, heappush, heappop
from model import StateMachine
from sensors import stepper, pump,force_sensor
from pyfirmata import Arduino, util
import time
import numpy as np
import cv2

stateMachine = StateMachine.StateMachine()
# movement_stack = []
seenTargets = set()

def retrack_target(old_frame,new_frame,old_bbox):
    new_bbox = stateMachine.object_tracker.get_new_object_position(old_frame,new_frame,old_bbox)
    if new_bbox is not None:
        print("Using Tracker")
        return new_bbox
    else:
        print("Using Other")
        frame = stateMachine.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        targets,scores = stateMachine.object_detection.get_target_scores(frame)
        max_score_indx = np.argmax(scores)
        return targets[max_score_indx]
        

def ShootTargets(frame,targets,scores):
    targets_minHeap = []
    camera_x,camera_y = frame.shape[1] // 2, frame.shape[0] // 2
    offset_x, offset_y = 0, 0
    for i in range(len(targets)):
        if scores[i] >= 0:
            heappush(targets_minHeap, (-1*scores[i], targets[i]))
    while targets_minHeap:
        _,bbox = heappop(targets_minHeap)
        target_x,target_y = stateMachine.object_detection.get_bbox_centroid(bbox)
        #Initial Move
        angle_x, dir_x = stepper.track_target_base(target_x-offset_x, camera_x, stateMachine.board)
        angle_y, dir_y = stepper.track_target_camera(target_y-offset_y, camera_y, stateMachine.board)
        #Find New Object Position
        new_frame = stateMachine.camera.capture_array()
        new_frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        new_bbox = retrack_target(frame,new_frame,bbox)
        # Adjust Movement
        new_target_x,new_target_y = stateMachine.object_detection.get_bbox_centroid(new_bbox)
        new_angle_x, new_dir_x = stepper.track_target_base(new_target_x-offset_x, camera_x, stateMachine.board)
        new_angle_y, new_dir_y = stepper.track_target_camera(new_target_y-offset_y, camera_y, stateMachine.board)
        #Go Back to the previous coordinate
        print(f"Initial Detection Angles: X {angle_x} ; Y {angle_y}")
        print(f"New Angles: X {new_angle_x} ; Y : {new_angle_y}")
        break
    exit()

def surveillance():
    for i in range(100):
        if stateMachine.state["camera_angle"] == -40  and stateMachine.state["camera_rotation_direction"] == "CW" and i != 0:
            break
        frame = stateMachine.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        targets, scores = stateMachine.object_detection.get_target_scores(frame)
        if targets and scores.all():
            ShootTargets(frame, targets, scores)
            break
        else:
            stateMachine.surveillance_camera()
    stateMachine.surveillance_base()
    time.sleep(1)
    

while True:
#     print("Surveilling")
    # force_sensor.check_liquid_level(board)
    # stepper.rotate_camera_stepper(60, "CCW",stateMachine.board)
    # stepper.rotate_base_stepper(60, "CCW",board)
    # stepper.rotate_camera_stepper(60, "CW",board)
    # stepper.rotate_base_stepper(60, "CW",board)

    # time.sleep(5)
    surveillance()
    # stateMachine.frame = stateMachine.camera.capture_array()
    # targets, scores = stateMachine.object_detection.get_target_scores(stateMachine.frame)
    # offset_x, offset_y = 0, 0
    # for i in range(len(targets)):
    #     if scores[i] >= 0:
    #         heappush(heap, (-1*scores[i], targets[i]))
    # for elem in heap:
    #     coordinates = stateMachine.object_detection.get_bbox_centroid(elem[1])
    #     if (stateMachine.state["frameIndex"], coordinates[0], coordinates[1]) in seenTargets:
    #         continue
    #     rows, cols, _ = stateMachine.frame.shape
    #     cx, cy = int(cols/2), int(rows/2)
    #     angle_x = stepper.track_base_stepper(coordinates[0]-offset_x, cx, stateMachine.board)
    #     angle_y = stepper.track_camera_stepper(coordinates[1]-offset_y, cy, stateMachine.board)
    #     stateMachine.state["base_angle"] += angle_x
    #     stateMachine.state["camera_angle"] += angle_y
    #     offset_x, offset_y = coordinates[0]-cx, coordinates[1]-cy
    #     pump.shoot_liquid(stateMachine.board)
    #     seenTargets.add((stateMachine.state["frameIndex"],coordinates[0], coordinates[1]))