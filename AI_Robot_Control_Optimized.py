# AI Robot Control (optimized skeleton)
# Replace ESP_IP and ESP_CAM_STREAM with your values.

import cv2
import mediapipe as mp
import socket

ESP_CAM_STREAM = "http://192.168.84.101:81/stream"
ESP_IP = "192.168.84.222"
PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
draw = mp.solutions.drawing_utils

pc = cv2.VideoCapture(0)
esp = cv2.VideoCapture(ESP_CAM_STREAM)

last_cmd = ""
water = False

def send(cmd):
    global last_cmd
    if cmd != last_cmd:
        sock.sendto(cmd.encode(), (ESP_IP, PORT))
        print("SEND:", cmd)
        last_cmd = cmd

def count(hand):
    fingers = 0
    if hand.landmark[4].x < hand.landmark[3].x:
        fingers += 1
    for t in [8,12,16,20]:
        if hand.landmark[t].y < hand.landmark[t-2].y:
            fingers += 1
    return fingers

while True:
    ok,img = pc.read()
    if not ok:
        continue

    img = cv2.flip(img,1)
    rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)

    cmd = None

    if res.multi_hand_landmarks:
        hand = res.multi_hand_landmarks[0]
        draw.draw_landmarks(img,hand,mp_hands.HAND_CONNECTIONS)
        total = count(hand)

        if total == 0:
            cmd = "S"
            water = False
        elif total == 1:
            cmd = "F"
        elif total == 2:
            cmd = "B"
        elif total == 3:
            cmd = "R"
        elif total == 4:
            cmd = "L"
        elif total == 5:
            if not water:
                cmd = "W"
                water = True

        cv2.putText(img,f"FINGERS:{total}",(10,40),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
    else:
        cmd = "S"

    if cmd:
        send(cmd)

    cv2.imshow("PC CAMERA",img)

    ok2,espimg = esp.read()
    if ok2:
        cv2.imshow("ESP32-CAM",espimg)

    if cv2.waitKey(1)&0xFF==27:
        break

pc.release()
esp.release()
cv2.destroyAllWindows()
