from heapq import heapify, heappush, heappop
from model import StateMachine
from sensors import stepper, pump

CNN_PATH = ""

stateMachine = StateMachine.StateMachine(cnn_data_path=CNN_PATH)
surveillanceDir = True
seenTargets = set()
while True:
    if (surveillanceDir):
        stateMachine.surveillance_base()
    else:
        stateMachine.surveillance_camera()
    heap = []
    heapify(heap)
    surveillanceDir = not surveillanceDir
    stateMachine.frame = stateMachine.camera.capture_array()
    targets, scores = stateMachine.object_detection.get_target_scores(stateMachine.frame)
    offset_x, offset_y = 0, 0
    for i in range(len(targets)):
        if scores[i] >= 0:
            heappush(heap, (-1*scores[i], targets[i]))
    for elem in heap:
        coordinates = stateMachine.object_detection.get_bbox_centroid(elem[1])
        if (stateMachine.state["frameIndex"], coordinates[0], coordinates[1]) in seenTargets:
            continue
        rows, cols, _ = stateMachine.frame.shape
        cx, cy = int(cols/2), int(rows/2)
        angle_x = stepper.track_base_stepper(coordinates[0]-offset_x, cx, stateMachine.board)
        angle_y = stepper.track_camera_stepper(coordinates[1]-offset_y, cy, stateMachine.board)
        stateMachine.state["base_angle"] += angle_x
        stateMachine.state["camera_angle"] += angle_y
        offset_x, offset_y = coordinates[0]-cx, coordinates[1]-cy
        pump.shoot_liquid(stateMachine.board)
        seenTargets.add((stateMachine.state["frameIndex"],coordinates[0], coordinates[1]))