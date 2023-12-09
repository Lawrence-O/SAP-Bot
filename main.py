from heapq import heapify, heappush, heappop
from model import StateMachine
from sensors import stepper, pump,force_sensor
from pyfirmata import Arduino, util
import time

stateMachine = StateMachine.StateMachine()

seenTargets = set()

def checkForTargets(frame):
    targets, scores = stateMachine.object_detection.get_target_scores(frame)
    targets_minHeap = heapify([])
    offset_x, offset_y = 0, 0
    for i in range(len(targets)):
        if scores[i] >= 0:
            heappush(targets_minHeap, (-1*scores[i], targets[i]))
    for elem in targets_minHeap:
        coordinates = stateMachine.object_detection.get_bbox_centroid(elem[1])
        if (stateMachine.state["frameIndex"], coordinates[0], coordinates[1]) in seenTargets:
            continue
        rows, cols, _ = frame.shape
        cx, cy = int(cols/2), int(rows/2)
        angle_x = stepper.track_base_stepper(coordinates[0]-offset_x, cx, stateMachine.board)
        angle_y = stepper.track_camera_stepper(coordinates[1]-offset_y, cy, stateMachine.board)
        stateMachine.state["base_angle"] += angle_x
        stateMachine.state["camera_angle"] += angle_y
        offset_x, offset_y = coordinates[0]-cx, coordinates[1]-cy
        # pump.shoot_liquid(stateMachine.board)
        seenTargets.add((stateMachine.state["frameIndex"],coordinates[0], coordinates[1]))


def surveillance():
    for i in range(100):
        if stateMachine.state["camera_angle"] == -40  and stateMachine.state["camera_rotation_direction"] == "CW" and i != 0:
            break
        stateMachine.surveillance_camera()
        frame = stateMachine.camera.capture_array()
        checkForTargets(frame)
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