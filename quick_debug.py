#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速手势调试工具
最简化的诊断工具
"""

import cv2
import mediapipe as mp
import numpy as np

def quick_test():
    """快速测试手部检测和简单手势识别"""
    print("Quick Gesture Debug")
    print("=" * 20)
    
    # 初始化
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
    
    # 打开摄像头
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Cannot open camera!")
        return
    
    print("Camera opened. Show your hand...")
    
    frame_count = 0
    detections = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 手部检测
            results = hands.process(rgb_frame)
            
            # 基本显示
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            
            if results.multi_hand_landmarks:
                detections += 1
                cv2.putText(frame, "HAND FOUND!", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # 简单的捏合检测
                hand_landmarks = results.multi_hand_landmarks[0]
                thumb = hand_landmarks.landmark[4]
                index = hand_landmarks.landmark[8]
                
                # 计算距离
                distance = np.sqrt((thumb.x - index.x)**2 + (thumb.y - index.y)**2)
                cv2.putText(frame, f"Distance: {distance:.3f}", (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                
                # 捏合判断
                if distance < 0.08:
                    cv2.putText(frame, "PINCH!", (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                # 显示关键点坐标
                cv2.putText(frame, f"T({thumb.x:.2f},{thumb.y:.2f})", (10, 190), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 1)
                cv2.putText(frame, f"I({index.x:.2f},{index.y:.2f})", (10, 210), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
                
            else:
                cv2.putText(frame, "NO HAND", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow('Quick Debug', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
    
    print(f"\nResults:")
    print(f"Frames processed: {frame_count}")
    print(f"Hand detections: {detections}")
    if frame_count > 0:
        rate = (detections / frame_count) * 100
        print(f"Detection rate: {rate:.1f}%")

if __name__ == "__main__":
    quick_test()