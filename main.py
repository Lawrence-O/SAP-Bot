from heapq import heapify, heappush, heappop
from model import StateMachine
from sensors import stepper, pump,force_sensor
from pyfirmata import Arduino, util
import time
import numpy as np
import cv2

stateMachine = StateMachine.StateMachine()

seenTargets = set()

def getNewTargetCoordinates(oldFrame, newFrame, bbox):
    new_bbox = stateMachine.object_tracker.get_new_object_position(oldFrame, newFrame, bbox)
    target_x,target_y = stateMachine.object_detection.get_bbox_centroid(new_bbox)
    return target_x, target_y


def checkForTargets(frame):
    targets, scores = stateMachine.object_detection.get_target_scores(frame)
    targets_minHeap = []
    camera_x,camera_y = frame.shape[1] // 2, frame.shape[0] // 2
   
    for i in range(len(targets)):
        if scores[i] >= 0:
            heappush(targets_minHeap, (-1*scores[i], targets[i]))
    while targets_minHeap:
        score,bbox = heappop(targets_minHeap)
        offset_x, offset_y = 0, 0
        target_x,target_y = stateMachine.object_detection.get_bbox_centroid(bbox)
        if (target_x > camera_x and target_y > camera_y):
            stepper.rotate_base_stepper(1, 'CW', stateMachine.board)
            stepper.rotate_camera_stepper(1, 'CW', stateMachine.board)
            new_frame = stateMachine.camera.capture_array()
            new_x, new_y = getNewTargetCoordinates(frame, new_frame, bbox)
            stepper.rotate_base_stepper((new_x-camera_x)/(target_x-new_x), 'CW', stateMachine.board)
            stepper.rotate_camera_stepper((new_y-camera_y)/(target_y-new_y), 'CW', stateMachine.board)
            time.sleep(2)
            stepper.rotate_base_stepper((new_x-camera_x)/(target_x-new_x)+1, 'CCW', stateMachine.board)
            stepper.rotate_camera_stepper((new_y-camera_y)/(target_y-new_y)+1, 'CCW', stateMachine.board)
        elif (target_x > camera_x):
            stepper.rotate_base_stepper(1, 'CW', stateMachine.board)
            stepper.rotate_camera_stepper(1, 'CCW', stateMachine.board)
            new_frame = stateMachine.camera.capture_array()
            new_x, new_y = getNewTargetCoordinates(frame, new_frame, bbox)
            stepper.rotate_base_stepper((new_x-camera_x)/(target_x-new_x), 'CW', stateMachine.board)
            stepper.rotate_camera_stepper((camera_y-new_y)/(new_y-target_y), 'CCW', stateMachine.board)
            time.sleep(2)
            stepper.rotate_base_stepper((new_x-camera_x)/(target_x-new_x)+1, 'CCW', stateMachine.board)
            stepper.rotate_camera_stepper((camera_y-new_y)/(new_y-target_y)+1, 'CW', stateMachine.board)
        elif (target_y > camera_y):
            stepper.rotate_base_stepper(1, 'CCW', stateMachine.board)
            stepper.rotate_camera_stepper(1, 'CW', stateMachine.board)
            new_frame = stateMachine.camera.capture_array()
            new_x, new_y = getNewTargetCoordinates(frame, new_frame, bbox)
            stepper.rotate_base_stepper((camera_x-new_x)/(new_x-target_x), 'CCW', stateMachine.board)
            stepper.rotate_camera_stepper((new_y-camera_y)/(target_y-new_y), 'CW', stateMachine.board)
            time.sleep(2)
            stepper.rotate_base_stepper((camera_x-new_x)/(new_x-target_x)+1, 'CW', stateMachine.board)
            stepper.rotate_camera_stepper((new_y-camera_y)/(target_y-new_y)+1, 'CCW', stateMachine.board)
            
        else:
            stepper.rotate_base_stepper(1, 'CCW', stateMachine.board)
            stepper.rotate_camera_stepper(1, 'CCW', stateMachine.board)
            new_frame = stateMachine.camera.capture_array()
            new_x, new_y = getNewTargetCoordinates(frame, new_frame, bbox)
            stepper.rotate_base_stepper((camera_x-new_x)/(new_x-target_x), 'CCW', stateMachine.board)
            stepper.rotate_camera_stepper((camera_y-new_y)/(new_y-target_y), 'CCW', stateMachine.board)
            time.sleep(2)
            stepper.rotate_base_stepper((camera_x-new_x)/(new_x-target_x)+1, 'CW', stateMachine.board)
            stepper.rotate_camera_stepper((camera_y-new_y)/(new_y-target_y)+1, 'CW', stateMachine.board)
        # angle_x = stepper.track_target_base(target_x-offset_x, camera_x, stateMachine.board)
        # angle_y = stepper.track_target_camera(target_y-offset_y, camera_y, stateMachine.board)

def surveillance():
    for i in range(100):
        if stateMachine.state["camera_angle"] == -40  and stateMachine.state["camera_rotation_direction"] == "CW" and i != 0:
            break
        frame = stateMachine.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        checkForTargets(frame)
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