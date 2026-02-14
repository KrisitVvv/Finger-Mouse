#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手势识别调试脚本
用于诊断和测试手势识别功能
"""

import cv2
import mediapipe as mp
import numpy as np
from recognition.gesture_recognizer import GestureRecognizer

def test_gesture_logic():
    """测试手势识别逻辑"""
    print("\n=== 手势逻辑测试 ===")
    
    # 创建模拟的关键点数据进行测试
    class MockLandmark:
        def __init__(self, x, y, z=0):
            self.x = x
            self.y = y
            self.z = z
    
    class MockHandLandmarks:
        def __init__(self):
            # 初始化一些典型的手势姿势
            self.landmark = [
                MockLandmark(0.5, 0.5),      # 0: WRIST
                MockLandmark(0.4, 0.4),      # 1: THUMB_CMC
                MockLandmark(0.3, 0.3),      # 2: THUMB_MCP
                MockLandmark(0.2, 0.2),      # 3: THUMB_IP
                MockLandmark(0.1, 0.1),      # 4: THUMB_TIP
                MockLandmark(0.5, 0.3),      # 5: INDEX_FINGER_MCP
                MockLandmark(0.5, 0.2),      # 6: INDEX_FINGER_PIP
                MockLandmark(0.5, 0.1),      # 7: INDEX_FINGER_DIP
                MockLandmark(0.5, 0.0),      # 8: INDEX_FINGER_TIP
                MockLandmark(0.6, 0.3),      # 9: MIDDLE_FINGER_MCP
                MockLandmark(0.6, 0.2),      # 10: MIDDLE_FINGER_PIP
                MockLandmark(0.6, 0.1),      # 11: MIDDLE_FINGER_DIP
                MockLandmark(0.6, 0.0),      # 12: MIDDLE_FINGER_TIP
                MockLandmark(0.7, 0.35),     # 13: RING_FINGER_MCP
                MockLandmark(0.7, 0.3),      # 14: RING_FINGER_PIP
                MockLandmark(0.7, 0.25),     # 15: RING_FINGER_DIP
                MockLandmark(0.7, 0.2),      # 16: RING_FINGER_TIP
                MockLandmark(0.8, 0.4),      # 17: PINKY_MCP
                MockLandmark(0.8, 0.35),     # 18: PINKY_PIP
                MockLandmark(0.8, 0.3),      # 19: PINKY_DIP
                MockLandmark(0.8, 0.25),     # 20: PINKY_TIP
            ]
    
    recognizer = GestureRecognizer()
    
    print("测试不同手势配置:")
    
    # 测试捏合手势
    mock_hand = MockHandLandmarks()
    is_pinch = recognizer._is_pinching(mock_hand)
    pinch_distance = ((mock_hand.landmark[4].x - mock_hand.landmark[8].x)**2 + 
                     (mock_hand.landmark[4].y - mock_hand.landmark[8].y)**2)**0.5
    print(f"捏合手势测试 - 距离: {pinch_distance:.3f}, 结果: {is_pinch}")
    
    # 测试握拳手势
    is_fist = recognizer._is_fist(mock_hand)
    print(f"握拳手势测试 - 结果: {is_fist}")
    
    # 测试V字手势
    is_victory = recognizer._is_victory_sign(mock_hand)
    print(f"V字手势测试 - 结果: {is_victory}")
    
    # 测试OK手势
    is_ok = recognizer._is_ok_sign(mock_hand)
    print(f"OK手势测试 - 结果: {is_ok}")
    
    # 测试完整识别流程
    print("\n完整手势识别测试:")
    recognized_gesture = recognizer.recognize_gesture(mock_hand)
    print(f"识别结果: {recognized_gesture}")

def analyze_gesture_thresholds():
    """分析和建议手势阈值"""
    print("\n=== 手势阈值分析 ===")
    
    recognizer = GestureRecognizer()
    print("当前阈值设置:")
    for gesture, threshold in recognizer.gesture_thresholds.items():
        print(f"  {gesture}: {threshold}")
    
    print("\n建议的阈值调整:")
    suggestions = {
        'pinch': 0.08,    # 增加捏合阈值，避免误识别
        'fist': 0.12,     # 增加握拳阈值，使握拳更容易识别
        'ok': 0.05        # 微调OK手势阈值
    }
    
    for gesture, suggested_value in suggestions.items():
        current = recognizer.gesture_thresholds[gesture]
        print(f"  {gesture}: {current} -> {suggested_value} ({'增加' if suggested_value > current else '减少'})")

if __name__ == "__main__":
    test_gesture_logic()
    analyze_gesture_thresholds()