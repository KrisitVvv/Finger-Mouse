#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试食指中指控制手势识别器
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recognition.gesture_recognizer import GestureRecognizer
import math

def test_gesture_recognizer():
    """测试手势识别器"""
    print("测试食指中指控制手势识别器...")
    
    # 创建手势识别器实例
    recognizer = GestureRecognizer()
    print(f"创建手势识别器成功")
    print(f"当前阈值设置: {recognizer.get_thresholds()}")
    
    # 测试方法是否存在
    print(f"\n测试方法存在性:")
    print(f"_finger_control_gesture_recognition 方法存在: {hasattr(recognizer, '_finger_control_gesture_recognition')}")
    print(f"recognize_gesture 方法存在: {hasattr(recognizer, 'recognize_gesture')}")
    print(f"get_hand_center 方法存在: {hasattr(recognizer, 'get_hand_center')}")
    
    # 测试阈值更新
    print(f"\n测试阈值更新:")
    recognizer.update_thresholds(
        pinch_threshold=0.07,
        fist_threshold=0.15,
        click_contact_threshold=0.06,
        finger_proximity_threshold=0.05
    )
    print(f"更新后阈值: {recognizer.get_thresholds()}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_gesture_recognizer()