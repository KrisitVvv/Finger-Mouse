#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实时手势识别调试工具
显示详细的手势识别过程和参数
"""

import cv2
import mediapipe as mp
import numpy as np
from recognition.gesture_recognizer import GestureRecognizer

def realtime_gesture_debug():
    """实时手势识别调试"""
    print("=== 实时手势识别调试 ===")
    print("按 'q' 退出, 'r' 重置历史, '+'/'-' 调整阈值")
    
    # 初始化MediaPipe
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    
    # 初始化手势识别器
    gesture_recognizer = GestureRecognizer()
    
    # 打开摄像头
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("错误: 无法打开摄像头")
        return
    
    frame_count = 0
    last_gesture = "无"
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 镜像翻转
            frame = cv2.flip(frame, 1)
            
            # BGR转RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 手部检测
            results = hands.process(frame_rgb)
            
            current_gesture = "无"
            debug_info = []
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # 绘制手部关键点
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=1)
                    )
                    
                    # 识别手势
                    current_gesture = gesture_recognizer.recognize_gesture(hand_landmarks)
                    
                    # 收集调试信息
                    if frame_count % 15 == 0:  # 每15帧更新一次详细信息
                        debug_info = collect_debug_info(hand_landmarks, gesture_recognizer)
            
            # 显示基本信息
            display_info(frame, current_gesture, frame_count, gesture_recognizer)
            
            # 显示调试信息
            if debug_info:
                display_debug_info(frame, debug_info)
            
            # 检测手势变化
            if current_gesture != last_gesture:
                print(f"手势变化: {last_gesture} -> {current_gesture}")
                last_gesture = current_gesture
            
            cv2.imshow('Real-time Gesture Debug', frame)
            
            # 键盘控制
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                gesture_recognizer.reset_history()
                print("手势历史已重置")
            elif key == ord('+'):
                adjust_thresholds(gesture_recognizer, increase=True)
            elif key == ord('-'):
                adjust_thresholds(gesture_recognizer, increase=False)
    
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"程序出错: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        print(f"调试结束，共处理 {frame_count} 帧")

def collect_debug_info(hand_landmarks, recognizer):
    """收集详细的调试信息"""
    info = []
    
    try:
        # 关键点坐标
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        wrist = hand_landmarks.landmark[0]
        
        info.append(f"拇指: ({thumb_tip.x:.3f}, {thumb_tip.y:.3f})")
        info.append(f"食指: ({index_tip.x:.3f}, {index_tip.y:.3f})")
        info.append(f"手腕: ({wrist.x:.3f}, {wrist.y:.3f})")
        
        # 距离计算
        pinch_dist = recognizer._calculate_distance(thumb_tip, index_tip)
        info.append(f"捏合距离: {pinch_dist:.3f}")
        
        # 手势判断详情
        info.append("--- 手势判断 ---")
        info.append(f"捏合: {pinch_dist < recognizer.gesture_thresholds['pinch']} "
                   f"(阈值: {recognizer.gesture_thresholds['pinch']})")
        
        # 握拳判断
        finger_tips = [8, 12, 16, 20]
        fist_distances = []
        for tip_idx in finger_tips:
            dist = recognizer._calculate_distance(hand_landmarks.landmark[tip_idx], wrist)
            fist_distances.append(dist)
        
        max_fist_dist = max(fist_distances) if fist_distances else 0
        info.append(f"握拳最大距离: {max_fist_dist:.3f} "
                   f"(阈值: {recognizer.gesture_thresholds['fist']})")
        info.append(f"握拳: {max_fist_dist <= recognizer.gesture_thresholds['fist']}")
        
        # 历史统计
        if len(recognizer.gesture_history) > 0:
            latest_gestures = recognizer.gesture_history[-5:]
            info.append(f"最近手势: {latest_gestures}")
            
    except Exception as e:
        info.append(f"调试信息收集错误: {e}")
    
    return info

def display_info(frame, gesture, frame_count, recognizer):
    """显示基本信息"""
    # 当前手势
    cv2.putText(frame, f"Current: {gesture}", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # 帧数
    cv2.putText(frame, f"Frame: {frame_count}", (10, 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # 阈值信息
    thresholds_text = f"P:{recognizer.gesture_thresholds['pinch']:.2f} "
    thresholds_text += f"F:{recognizer.gesture_thresholds['fist']:.2f} "
    thresholds_text += f"O:{recognizer.gesture_thresholds['ok']:.2f}"
    cv2.putText(frame, thresholds_text, (10, 90), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    # 控制说明
    cv2.putText(frame, "Keys: q-quit r-reset +/-adjust", (10, frame.shape[0]-20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

def display_debug_info(frame, debug_info):
    """显示调试信息"""
    y_pos = 120
    for i, info in enumerate(debug_info[:8]):  # 限制显示行数
        if y_pos < frame.shape[0] - 50:
            cv2.putText(frame, info, (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 255, 255), 1)
            y_pos += 20

def adjust_thresholds(recognizer, increase=True):
    """调整手势识别阈值"""
    delta = 0.01 if increase else -0.01
    
    # 调整所有阈值
    new_pinch = max(0.03, min(0.15, recognizer.gesture_thresholds['pinch'] + delta))
    new_fist = max(0.08, min(0.2, recognizer.gesture_thresholds['fist'] + delta * 1.5))
    new_ok = max(0.02, min(0.1, recognizer.gesture_thresholds['ok'] + delta))
    
    recognizer.update_thresholds(new_pinch, new_fist, new_ok)
    
    direction = "增加" if increase else "减少"
    print(f"阈值{direction}: P:{new_pinch:.3f} F:{new_fist:.3f} O:{new_ok:.3f}")

if __name__ == "__main__":
    realtime_gesture_debug()