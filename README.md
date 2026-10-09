\# DOFBot Hand Gesture Control



Control a Yahboom DOFBot robotic arm using hand gestures detected by MediaPipe from a laptop camera.



\## Features

\- Hand left/right → Base rotation

\- Thumb + Index pinch → Shoulder forward

\- Thumb + Middle pinch → Elbow down

\- Thumb + Ring pinch → Wrist down

\- Thumb + Pinky touch → Gripper open

\- Thumb + Pinky separate → Gripper close



\## Requirements



\### Laptop

\- Python 3.10 or 3.11

\- mediapipe==0.10.9

\- opencv-python

\- numpy



\### Jetson Nano

\- Yahboom DOFBot + Arm\_Lib



\## How to Run



\*\*On Jetson:\*\*

```bash

cd \~/pose\_control

python3 jetson\_gesture\_receiver.py



