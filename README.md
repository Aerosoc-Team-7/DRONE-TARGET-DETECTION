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

