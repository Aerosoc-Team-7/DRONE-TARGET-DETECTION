import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import cv2
import torch
import math
import time
from ultralytics import YOLO


SIMULATION_MODE = True  #ye Pi5 me false hoga 

if not SIMULATION_MODE:
    from adafruit_servokit import ServoKit
    kit = ServoKit(channels=16)
    PAN_CHANNEL = 0
    TILT_CHANNEL = 1
    kit.servo[PAN_CHANNEL].angle = 90
    kit.servo[TILT_CHANNEL].angle = 90


class PIDController:
    def __init__(self, kp, ki, kd, max_out=1.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_out = max_out
        self.prev_error = 0
        self.integral = 0
        self.last_time = time.time()

    def compute(self, error):
        current_time = time.time()
        dt = current_time - self.last_time
        if dt <= 0.0: dt = 0.01 

        proportional = self.kp * error
        self.integral += error * dt
        derivative = self.kd * (error - self.prev_error) / dt

        output = proportional + (self.ki * self.integral) + derivative
        output = max(min(output, self.max_out), -self.max_out)

        self.prev_error = error
        self.last_time = current_time
        return output


device = 'cpu'
model = YOLO('yolov8n.pt').to(device)
cap = cv2.VideoCapture(0)



FRAME_WIDTH, FRAME_HEIGHT = 640, 480
CENTER_X, CENTER_Y = FRAME_WIDTH // 2, FRAME_HEIGHT // 2
REF_AREA = 50000
ALPHA = 0.2



FOV_H = 62.2  
DEG_PER_PIXEL_X = (FOV_H / 2) / CENTER_X  # ~0.097 deg/pixel for 640px width


yaw_pid = PIDController(kp=0.02, ki=0.001, kd=0.01, max_out=1.0)
pitch_pid = PIDController(kp=0.00005, ki=0.000001, kd=0.00002, max_out=1.0)



smoothed_area = REF_AREA
locked_id = None
last_known_x, last_known_y = CENTER_X, CENTER_Y
vel_x, vel_y = 0, 0
frames_lost = 0
MAX_COAST_FRAMES = 30


pan_angle = 90.0



while True:
    ret, frame = cap.read()
    if not ret: break
    
    results = model.track(frame, persist=True, classes=[0], tracker="bytetrack.yaml", verbose=False)
    target_found_this_frame = False
    
    yaw_cmd = 0.0
    pitch_cmd = 0.0
    
    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xywh.cpu().numpy()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        
        
        if locked_id is None:
            min_dist = float('inf')
            for i, box in enumerate(boxes):
                x_t, y_t, w, h = box
                dist = math.hypot(x_t - CENTER_X, y_t - CENTER_Y)
                if dist < min_dist:
                    min_dist = dist
                    locked_id = track_ids[i]



        for i, track_id in enumerate(track_ids):
            if track_id == locked_id:
                target_found_this_frame = True
                frames_lost = 0 
                
                x_t, y_t, w, h = boxes[i]
                current_area = w * h
                
                vel_x = x_t - last_known_x
                vel_y = y_t - last_known_y
                last_known_x, last_known_y = x_t, y_t
                


                x_error_pixels = x_t - CENTER_X
                x_error_degrees = x_error_pixels * DEG_PER_PIXEL_X
                yaw_cmd = yaw_pid.compute(x_error_degrees)
                

                smoothed_area = (ALPHA * current_area) + ((1 - ALPHA) * smoothed_area)
                depth_error = REF_AREA - smoothed_area
                pitch_cmd = pitch_pid.compute(depth_error)
                

                top_left = (int(x_t - w/2), int(y_t - h/2))
                bottom_right = (int(x_t + w/2), int(y_t + h/2))
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                cv2.putText(frame, f"LOCKED ID: {locked_id}", (int(x_t), int(y_t)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                break 


#extrapolation
    if not target_found_this_frame and locked_id is not None:
        frames_lost += 1
        if frames_lost < MAX_COAST_FRAMES:
            pred_x = last_known_x + (vel_x * frames_lost)
            pred_x_deg = (pred_x - CENTER_X) * DEG_PER_PIXEL_X
            yaw_cmd = yaw_pid.compute(pred_x_deg)
            pitch_cmd = 0.0 
        else:
            locked_id = None
            smoothed_area = REF_AREA
            yaw_pid.integral = 0 
            pitch_pid.integral = 0



#ye woh angle conversion hai
    max_turn_rate = 5.0 
    pan_angle = pan_angle - (yaw_cmd * max_turn_rate)
    
#servo limits
    pan_angle = max(0.0, min(pan_angle, 180.0))

    if not SIMULATION_MODE:
        kit.servo[PAN_CHANNEL].angle = pan_angle
        # yaxis ka karna hoga yahan so add tilt

    cv2.drawMarker(frame, (CENTER_X, CENTER_Y), (255, 0, 0), cv2.MARKER_CROSS, 20, 2)
    cv2.putText(frame, f"TARGET PAN ANGLE: {pan_angle:.1f} deg", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(frame, f"PID OUT: {yaw_cmd:+.3f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    cv2.imshow("Drone Tracker (Hardware Ready)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()