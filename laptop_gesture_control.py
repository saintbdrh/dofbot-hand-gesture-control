import cv2
import mediapipe as mp
import numpy as np
import time
import socket
import json

# ========================= CONFIG =========================
JETSON_IP = "192.168.143.197"     # <<< Change to your Jetson IP
JETSON_PORT = 5000

SMOOTH_FACTOR = 0.82
CENTER = 90

BASE_RANGE     = (40, 140)
SHOULDER_RANGE = (50, 130)   # Lower = Shoulder FORWARD
ELBOW_RANGE    = (40, 150)
WRIST_RANGE    = (40, 140)
# =========================================================

print(f"Connecting to Jetson at {JETSON_IP}:{JETSON_PORT} ...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((JETSON_IP, JETSON_PORT))
print("✅ Connected!")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("\n🎮 Gesture Control Ready")
print("Hand left/right     → Base left/right")
print("Thumb + Index       → Shoulder FORWARD")
print("Thumb + Middle      → Elbow DOWN")
print("Thumb + Ring        → Wrist DOWN")
print("Thumb + Pinky touch → Gripper OPEN")
print("Thumb + Pinky apart → Gripper CLOSE")
print("Press 'q' to quit\n")

def distance(p1, p2):
    return np.hypot(p1.x - p2.x, p1.y - p2.y)

prev_base = CENTER
prev_shoulder = CENTER
prev_elbow = CENTER
prev_wrist = CENTER

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        base = CENTER
        shoulder = CENTER
        elbow = CENTER
        wrist = CENTER
        gripper = 30

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            lm = hand.landmark

            hand_x = lm[0].x
            base = int(np.interp(hand_x, [0.15, 0.85], BASE_RANGE))

            thumb_tip = lm[4]
            idx_tip   = lm[8]
            mid_tip   = lm[12]
            ring_tip  = lm[16]
            pinky_tip = lm[20]

            pinch_threshold = 0.085

            thumb_idx   = distance(thumb_tip, idx_tip)   < pinch_threshold
            thumb_mid   = distance(thumb_tip, mid_tip)   < pinch_threshold
            thumb_ring  = distance(thumb_tip, ring_tip)  < pinch_threshold
            thumb_pinky = distance(thumb_tip, pinky_tip) < pinch_threshold

            if thumb_idx:
                shoulder = SHOULDER_RANGE[0]
            if thumb_mid:
                elbow = ELBOW_RANGE[0]
            if thumb_ring:
                wrist = WRIST_RANGE[0]

            if thumb_pinky:
                gripper = 160
            else:
                gripper = 30

            base     = int(SMOOTH_FACTOR * prev_base     + (1 - SMOOTH_FACTOR) * base)
            shoulder = int(SMOOTH_FACTOR * prev_shoulder + (1 - SMOOTH_FACTOR) * shoulder)
            elbow    = int(SMOOTH_FACTOR * prev_elbow    + (1 - SMOOTH_FACTOR) * elbow)
            wrist    = int(SMOOTH_FACTOR * prev_wrist    + (1 - SMOOTH_FACTOR) * wrist)

            prev_base     = base
            prev_shoulder = shoulder
            prev_elbow    = elbow
            prev_wrist    = wrist

            data = {
                "base": base,
                "shoulder": shoulder,
                "elbow": elbow,
                "wrist": wrist,
                "gripper": gripper
            }
            sock.sendall((json.dumps(data) + "\n").encode())

            mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            cv2.putText(frame, f"Base: {base}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            cv2.putText(frame, 