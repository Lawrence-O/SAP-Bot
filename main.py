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
        print("Using Detections")
        frame = stateMachine.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        targets,scores = stateMachine.object_detection.get_target_scores(frame)
        if targets:
            max_score_indx = np.argmax(scores)
            return targets[max_score_indx]
    return None  

def ShootTargets(frame,targets,scores):
    targets_minHeap = []
    camera_x,camera_y = frame.shape[1] // 2, frame.shape[0] // 2
    offset_x, offset_y = 0, 0
    for i in range(len(targets)):
        if scores[i] >= 0:
            heappush(targets_minHeap, (-1*scores[i], targets[i]))
    print("Minheap: ",targets_minHeap)
    while targets_minHeap:
        _,bbox = heappop(targets_minHeap)
        target_x,target_y = stateMachine.object_detection.get_bbox_centroid(bbox)
        #Initial Move
        angle_x, dir_x = stepper.track_target_base(target_x-offset_x, camera_x, stateMachine.board)
        angle_y, dir_y = stepper.track_target_camera(target_y-offset_y, camera_y, stateMachine.board)
        print(f"Initial Detection Angles: X {angle_x} ; Y {angle_y}")
        #Find New Object Position
        new_frame = stateMachine.camera.capture_array()
        new_frame = cv2.cvtColor(new_frame, cv2.COLOR_RGBA2RGB)
        new_bbox = retrack_target(frame,new_frame,bbox)
        total_x, total_y = 0, 0
        if (new_bbox is not None):
            # Adjust Movement
            new_target_x,new_target_y = stateMachine.object_detection.get_bbox_centroid(new_bbox)
            new_angle_x, new_dir_x = stepper.track_target_base(new_target_x-offset_x, camera_x, stateMachine.board)
            new_angle_y, new_dir_y = stepper.track_target_camera(new_target_y-offset_y, camera_y, stateMachine.board)
            print(f"New Angles: X {new_angle_x} ; Y : {new_angle_y}")
            if new_dir_x == "CCW":
                total_x += new_angle_x
            else:
                total_x -= new_angle_x

            if new_dir_y == "CCW":
                total_y += new_angle_y
            else:
                total_y -= new_angle_y
        #Go Back to the previous coordinate
        for _ in range(100):
            force_sensor.check_liquid_level(stateMachine.board)
        # stepper.rotate_base_stepper(8, 'CW', stateMachine.board)
        # stepper.rotate_camera_stepper(5, 'CCW', stateMachine.board)
        pump.shoot_liquid(stateMachine.board)
        time.sleep(0.5)
        if dir_x == "CCW":
            total_x += angle_x
        else:
            total_x -= angle_x

        if dir_y == "CCW":
            total_y += angle_y
        else:
            total_y -= angle_y
        
        if total_x >= 0:
            stepper.rotate_base_stepper(total_x, 'CCW', stateMachine.board)
        else:
            stepper.rotate_base_stepper(abs(total_x), 'CW', stateMachine.board)
        if total_y >= 0:
            stepper.rotate_camera_stepper(total_y, 'CCW', stateMachine.board)
        else:
            stepper.rotate_camera_stepper(abs(total_y), 'CW', stateMachine.board)
    # exit()

def surveillance():
    for i in range(100):
        frame = stateMachine.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        targets, scores = stateMachine.object_detection.get_target_scores(frame)
        if targets:
            return frame, targets, scores
        if stateMachine.state["camera_angle"] == -40  and stateMachine.state["camera_rotation_direction"] == "CW" and i != 0:
            break
        stateMachine.surveillance_camera()
    stateMachine.surveillance_base()
    time.sleep(0.01)
    return (None,None,None)
    
while True:
    for _ in range(100):
        force_sensor.check_liquid_level(stateMachine.board)
#     print("Surveilling")
    # force_sensor.check_liquid_level(board)
    # stepper.rotate_camera_stepper(60, "CCW",stateMachine.board)
    # stepper.rotate_base_stepper(60, "CCW",board)
    # stepper.rotate_camera_stepper(60, "CW",board)
    # stepper.rotate_base_stepper(60, "CW",board)

    # time.sleep(5)
    frame, targets, scores = surveillance()
    if frame is None or targets is None or scores is None:
        print("isNONE")
        continue
    else:
        print("TARGETs and Scores")
        print(targets, scores)
   
    ShootTargets(frame,targets,scores)
    # time.sleep(1)
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