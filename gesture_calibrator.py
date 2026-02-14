#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手势识别校准工具
帮助用户校准手势识别参数并测试准确性
"""

import cv2
import mediapipe as mp
import numpy as np
from recognition.gesture_recognizer import GestureRecognizer

def run_calibration():
    """运行手势校准"""
    print("Gesture Calibration Tool")
    print("=" * 30)
    
    # 初始化MediaPipe
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    
    recognizer = GestureRecognizer()
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    print("Camera opened successfully")
    print("Instructions:")
    print("- Make different gestures to test recognition")
    print("- Press SPACE to freeze frame for analysis")
    print("- Press 'q' to quit")
    print("- Current thresholds:")
    for gesture, threshold in recognizer.gesture_thresholds.items():
        print(f"  {gesture}: {threshold:.3f}")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 镜像翻转
            frame = cv2.flip(frame, 1)
            
            # BGR转RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 手部检测
            results = hands.process(frame_rgb)
            current_gesture = "None"
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # 绘制手部关键点
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=1)
                    )
                    
                    # 识别手势
                    current_gesture = recognizer.recognize_gesture(hand_landmarks)
                    
                    # 显示关键点信息
                    thumb_tip = hand_landmarks.landmark[4]
                    index_tip = hand_landmarks.landmark[8]
                    distance = np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
                    
                    cv2.putText(frame, f"Distance: {distance:.3f}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                    cv2.putText(frame, f"Threshold: {recognizer.gesture_thresholds['pinch']:.3f}", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 100), 1)
            
            # 显示信息
            cv2.putText(frame, f"Gesture: {current_gesture}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            cv2.imshow('Gesture Calibration', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):  # 空格键冻结帧
                print(f"\nFrozen Frame Analysis:")
                print(f"Current gesture: {current_gesture}")
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        thumb_tip = hand_landmarks.landmark[4]
                        index_tip = hand_landmarks.landmark[8]
                        distance = np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
                        print(f"Pinch distance: {distance:.3f}")
                        print(f"Is pinch (threshold {recognizer.gesture_thresholds['pinch']:.3f}): {distance < recognizer.gesture_thresholds['pinch']}")
                
                cv2.waitKey(0)  # 等待按键继续
    
    except Exception as e:
        print(f"Error during calibration: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        print("Calibration finished")

if __name__ == "__main__":
    run_calibration()