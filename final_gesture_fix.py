#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终手势识别修复方案
直接修改主程序中的手势识别逻辑
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, Optional
import time

class FixedGestureRecognizer:
    """修复版手势识别器"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # 简化且合理的阈值
        self.thresholds = {
            'pinch': 0.08,    # 捏合
            'fist': 0.12,     # 握拳
            'ok': 0.06        # OK手势
        }
        
        self.last_gesture = "None"
        self.stable_count = 0
        self.stability_required = 3
    
    def process_frame(self, frame) -> Tuple[np.ndarray, str]:
        """处理单帧并识别手势"""
        try:
            # 镜像翻转
            frame = cv2.flip(frame, 1)
            
            # BGR转RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 手部检测
            results = self.hands.process(rgb_frame)
            
            current_gesture = "None"
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # 绘制关键点
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=1)
                    )
                    
                    # 识别手势
                    current_gesture = self._recognize_gesture_simple(hand_landmarks)
            
            # 稳定性处理
            if current_gesture == self.last_gesture:
                self.stable_count += 1
            else:
                self.stable_count = 1
                self.last_gesture = current_gesture
            
            final_gesture = current_gesture if self.stable_count >= self.stability_required else "None"
            
            # 显示信息
            cv2.putText(frame, f"Gesture: {final_gesture}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Stable: {self.stable_count}/{self.stability_required}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            
            return frame, final_gesture
            
        except Exception as e:
            print(f"Frame processing error: {e}")
            return frame, "None"
    
    def _recognize_gesture_simple(self, hand_landmarks) -> str:
        """简化的手势识别逻辑"""
        try:
            # 获取关键点
            thumb_tip = hand_landmarks.landmark[4]   # 拇指尖
            index_tip = hand_landmarks.landmark[8]   # 食指尖
            middle_tip = hand_landmarks.landmark[12] # 中指尖
            wrist = hand_landmarks.landmark[0]       # 手腕
            
            # 计算捏合距离
            pinch_distance = np.sqrt((thumb_tip.x - index_tip.x)**2 + 
                                   (thumb_tip.y - index_tip.y)**2)
            
            # 计算手指弯曲程度
            finger_tips = [8, 12, 16, 20]  # 食指、中指、无名指、小指
            bent_fingers = 0
            
            for tip_id in finger_tips:
                tip = hand_landmarks.landmark[tip_id]
                distance = np.sqrt((tip.x - wrist.x)**2 + (tip.y - wrist.y)**2)
                if distance < self.thresholds['fist']:
                    bent_fingers += 1
            
            # 手势判断（按优先级）
            if pinch_distance < self.thresholds['pinch']:
                return "Pinch"
            elif bent_fingers >= 3:  # 大部分手指弯曲
                return "Fist"
            elif pinch_distance < self.thresholds['ok']:
                return "OK"
            else:
                return "Open Palm"
                
        except Exception as e:
            print(f"Gesture recognition error: {e}")
            return "None"
    
    def cleanup(self):
        """清理资源"""
        try:
            self.hands.close()
        except:
            pass

def run_fixed_gesture_recognition():
    """运行修复后的手势识别"""
    print("Fixed Gesture Recognition System")
    print("=" * 35)
    
    recognizer = FixedGestureRecognizer()
    
    # 打开摄像头
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Cannot open camera!")
        return
    
    print("System started. Press 'q' to quit.")
    print("Current thresholds:")
    for name, value in recognizer.thresholds.items():
        print(f"  {name}: {value}")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 处理帧
            processed_frame, gesture = recognizer.process_frame(frame)
            
            cv2.imshow('Fixed Gesture Recognition', processed_frame)
            
            # 检测手势变化
            if gesture != "None" and gesture != recognizer.last_gesture:
                print(f"Gesture detected: {gesture}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        recognizer.cleanup()
        print("System stopped.")

if __name__ == "__main__":
    run_fixed_gesture_recognition()