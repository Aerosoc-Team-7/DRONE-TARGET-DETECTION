import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import cv2
import torch
import math
from ultralytics import YOLO

# ---------------- MODEL ----------------
device = 'cpu'
model = YOLO('/models/yolov8n.pt').to(device)
cap = cv2.VideoCapture(0)

FRAME_WIDTH, FRAME_HEIGHT = 640, 480
CENTER_X, CENTER_Y = FRAME_WIDTH // 2, FRAME_HEIGHT // 2

# ---------------- TRACK STATE ----------------
locked_id = None
last_x, last_y = CENTER_X, CENTER_Y
last_area = 0

dx, dy = 0, 0

lost_frames = 0
MAX_LOST = 60
search_mode = False

# thresholds
MOVE_THRESH = 5
AREA_THRESH = 800


# ---------------- DIRECTION FUNCTION ----------------
def get_direction(dx, dy, d_area):
    direction = ""

    if dx > MOVE_THRESH:
        direction += "→"
    elif dx < -MOVE_THRESH:
        direction += "←"

    if dy > MOVE_THRESH:
        direction += "↓"
    elif dy < -MOVE_THRESH:
        direction += "↑"

    if d_area > AREA_THRESH:
        direction += " (CLOSER)"
    elif d_area < -AREA_THRESH:
        direction += " (AWAY)"

    return direction if direction != "" else "STABLE"


# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, persist=True, classes=[0],
                          tracker="bytetrack.yaml", verbose=False)

    target_found = False

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xywh.cpu().numpy()
        track_ids = results[0].boxes.id.int().cpu().tolist()

        # -------- INITIAL LOCK --------
        if locked_id is None:
            min_dist = float('inf')
            for i, box in enumerate(boxes):
                x, y, w, h = box
                dist = math.hypot(x - CENTER_X, y - CENTER_Y)
                if dist < min_dist:
                    min_dist = dist
                    locked_id = track_ids[i]

        # -------- FIND LOCKED TARGET --------
        for i, tid in enumerate(track_ids):
            if tid == locked_id:
                target_found = True
                lost_frames = 0
                search_mode = False

                x, y, w, h = boxes[i]
                area = w * h

                # motion
                dx = x - last_x
                dy = y - last_y
                d_area = area - last_area

                direction = get_direction(dx, dy, d_area)

                last_x, last_y = x, y
                last_area = area

                # draw box
                cv2.rectangle(frame,
                              (int(x - w/2), int(y - h/2)),
                              (int(x + w/2), int(y + h/2)),
                              (0, 255, 0), 2)

                # draw arrow
                scale = 4
                end_x = int(x + dx * scale)
                end_y = int(y + dy * scale)

                cv2.arrowedLine(frame,
                                (int(x), int(y)),
                                (end_x, end_y),
                                (0, 0, 255), 3)

                # text
                cv2.putText(frame, f"ID: {locked_id}",
                            (int(x), int(y) - 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 0), 2)

                cv2.putText(frame, f"MOVE: {direction}",
                            (int(x), int(y) - 15),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 0, 255), 2)

                break

        # -------- RE-LOCK IN SEARCH MODE --------
        if not target_found and search_mode:
            min_dist = float('inf')
            best_idx = -1

            for i, box in enumerate(boxes):
                x_t, y_t, w, h = box
                dist = math.hypot(x_t - last_x, y_t - last_y)

                if dist < min_dist:
                    min_dist = dist
                    best_idx = i

            if best_idx != -1:
                locked_id = track_ids[best_idx]
                target_found = True
                search_mode = False

    # -------- LOST HANDLING --------
    if not target_found and locked_id is not None:
        lost_frames += 1

        if lost_frames < MAX_LOST:
            # prediction
            pred_x = int(last_x + dx)
            pred_y = int(last_y + dy)

            cv2.circle(frame, (pred_x, pred_y), 8, (0, 255, 255), -1)
            cv2.putText(frame, "PREDICTING...",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 255), 2)

        else:
            search_mode = True
            cv2.putText(frame, "SEARCHING...",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 0, 255), 2)

    # -------- CENTER MARK --------
    cv2.drawMarker(frame, (CENTER_X, CENTER_Y),
                   (255, 0, 0), cv2.MARKER_CROSS, 20, 2)

    cv2.imshow("Robust 3D Motion Tracker", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()