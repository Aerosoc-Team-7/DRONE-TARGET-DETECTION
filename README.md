<<<<<<< HEAD
# DRONE-TARGET-DETECTION
# Autonomous Drone Tracking System

**Aerospace Society (Aerosoc)**

This repository contains the software pipeline for an autonomous target-tracking drone. Designed to run on a Raspberry Pi 3 or 4, the system uses YOLOv8n AI to identify a human target and calculates the exact mathematical flight commands needed to follow them.

## ✨ Key Features

* **Smart Target Locking:** Uses ByteTrack to assign a unique ID to a specific target, ignoring background noise and other people in the frame.
* **Path Extrapolation:** If the target is temporarily hidden or leaves the camera frame, the system predicts their path using their last known velocity for up to 30 frames.
* **Dynamic Depth Estimation:** Calculates forward and backward movement commands based on the scaling of the target's bounding box area relative to a calibrated reference distance.
* **Simulation Mode:** Run and test the entire flight tracking logic on a local laptop webcam before deploying it to the physical drone.

---

## 🚀 System Pipeline

The software operates in a continuous, real-time loop:

1. **Detection:** A 2D camera feed is processed through the YOLOv8n model to locate the target.
2. **Conversion:** The pixel error (distance between the target and the center of the camera) is converted into real-world degrees ($0.1036^\circ$/pixel).
3. **Calculation:** A tuned PID controller processes this error alongside the depth-estimation algorithm to generate smooth Yaw (left/right) and Pitch (forward/backward) commands.

---

## 🛠️ Installation

Ensure you have Python 3.8+ installed. It is highly recommended to use a virtual environment to prevent package conflicts.

```bash
# Clone the repository
git clone https://github.com/Aerosoc-Team-7/DRONE-TARGET-DETECTION.git
cd drone-tracking

# Install dependencies
pip install -r requirements.txt

```

> **Note:** The `ultralytics` package inside the requirements file will automatically handle the installation of PyTorch and its related dependencies.

---

## 💻 Usage

To test the tracking algorithms and PID math using your local webcam:

1. Open `tracker.py` in your code editor.
2. Ensure `SIMULATION_MODE = True` at the top of the file.
3. Run the script from your terminal:

```bash
python tracker.py

```

A visual telemetry window will open, displaying the bounding box, target ID, extrapolated flight path, and live PID output calculations. Press `q` to quit the window.

---

## 🗺️ Roadmap

* [x] Integrate YOLOv8n object detection.
* [x] Implement ByteTrack for ID locking and memory extrapolation.
* [x] Convert pixel error to angular displacement (FOV Math).
* [x] Implement Yaw and Pitch PID Controllers.
* [ ] Map the Y-axis (Altitude) error to a third PID controller for full 3D tracking.
* [ ] Integrate hardware outputs for the Raspberry Pi 3/4.

=======
# Drone Target Detection & Tracking System

A real-time computer vision project that detects, tracks, and follows a target using **YOLOv8** and a **PID-controlled pan–tilt system**. The system is designed to run in two modes:

* **Simulation Mode** – runs on a normal computer using a webcam.
* **Hardware Mode** – runs on a Raspberry Pi with servo motors controlling a pan–tilt mechanism.

The goal of the project is to automatically detect a target (such as a person or drone), track it across frames, and control servos to keep the target centered in the camera's field of view.

---

# Features

## 1. Real-Time Object Detection

The system uses **YOLOv8** to detect objects in real time from a camera feed.

* Runs on CPU for compatibility
* Processes frames from a webcam
* Detects and extracts bounding boxes for objects

---

## 2. Multi-Object Tracking

The system uses **ByteTrack** tracking to assign IDs to detected objects.

This allows:

* Tracking objects across multiple frames
* Maintaining identity of targets
* Selecting and locking onto a specific target

---

## 3. Automatic Target Locking

When multiple objects are detected:

* The system automatically selects the object **closest to the center of the frame**
* That object becomes the **locked target**
* Tracking continues using its **unique tracking ID**

This ensures stable tracking without switching between targets.

---

## 4. Persistent Target Lock (Planned Feature)

A new feature will ensure the system **never switches targets** automatically.

Behavior:

1. When a target is locked, its **tracking ID is stored**.
2. If the target temporarily leaves the frame:

   * The system **does not lock onto any new target**.
3. When the original target reappears:

   * The system **relocks onto the same target ID**.

This prevents incorrect target switching in crowded scenes.

---

## 5. PID-Based Target Following

The system uses **PID controllers** to smoothly follow the target.

Two PID loops are used:

### Yaw Controller

Controls horizontal rotation (pan).

* Error calculated in **degrees from center**
* Adjusts servo angle to keep target centered

### Pitch Controller

Controls vertical alignment using **object size (depth approximation)**.

* Larger bounding box → target is closer
* Smaller bounding box → target is farther

---

## 6. Target Motion Prediction

If the target temporarily disappears:

* The system **predicts its next position** using velocity.
* Tracking continues for a short period using extrapolation.
* If the target does not reappear within a defined number of frames, the lock resets.

This prevents sudden loss of tracking due to short occlusions.

---

## 7. Servo Control (Hardware Mode)

When running on Raspberry Pi:

* Servo motors control a **pan–tilt camera mount**
* Controlled using **Adafruit ServoKit**
* Supports 16 PWM channels

Current implementation:

* **Pan (Yaw) axis implemented**
* **Tilt axis planned**

---

## 8. Simulation Mode

The project can run without hardware using:

```
SIMULATION_MODE = True
```

In this mode:

* No servo hardware is required
* Pan angle values are simulated
* Debug information is displayed on the screen

---

# System Architecture

Camera → YOLOv8 Detection → ByteTrack Tracking → Target Selection → PID Control → Servo Movement

Pipeline steps:

1. Capture frame from webcam
2. Detect objects using YOLOv8
3. Assign tracking IDs with ByteTrack
4. Lock onto a target
5. Compute error relative to frame center
6. Use PID controller to compute movement
7. Convert movement to servo angle
8. Move pan–tilt hardware

---

# Visual Feedback

The system displays:

* Bounding box around the locked target
* Target tracking ID
* Crosshair showing camera center
* Current servo pan angle
* PID controller output

This helps with debugging and tuning.

---

# Technologies Used

* Python
* YOLOv8
* OpenCV
* PyTorch
* ByteTrack
* Adafruit ServoKit (hardware mode)

---

# Project Structure

```
drone-target-detection/
│
├── main.py
├── README.md
├── requirements.txt
└── models/
```

---

# Future Improvements

Planned upgrades include:

* Persistent target ID locking
* Vertical tilt servo control
* Faster inference using GPU / TensorRT
* Target re-identification
* Improved motion prediction (Kalman Filter)
* Support for drone-specific detection models
* Raspberry Pi optimization

---

# Requirements

Typical dependencies include:

```
ultralytics
opencv-python
torch
numpy
adafruit-circuitpython-servokit
```

Install using:

```
pip install -r requirements.txt
```

---

# Running the Project

### 1. Create virtual environment

```
python -m venv .venv
```

### 2. Activate environment

Windows:

```
.venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Run the program

```
python main.py
```

Press **Q** to quit the program.

---

# Example Use Cases

* Autonomous drone tracking
* Security monitoring systems
* Robotics vision systems
* AI-assisted turret tracking
* Smart surveillance cameras

---

# License

This project is intended for educational and research purposes.
>>>>>>> c5da950fce1dfa1929cd5f5151e352f02d7b8fd0
