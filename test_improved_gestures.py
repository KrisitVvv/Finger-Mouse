#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试改进后的手势识别功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recognition.gesture_recognizer import GestureRecognizer

def test_improved_recognizer():
    """测试改进后的手势识别器"""
    print("=== 测试改进后的手势识别器 ===")
    
    recognizer = GestureRecognizer()
    
    # 测试数据生成函数
    def create_mock_hand(**kwargs):
        """创建模拟手部关键点"""
        class MockLandmark:
            def __init__(self, x, y, z=0):
                self.x = x
                self.y = y
                self.z = z
        
        class MockHandLandmarks:
            def __init__(self, positions):
                self.landmark = [MockLandmark(x, y) for x, y in positions]
        
        # 默认手部位置
        default_positions = [
            (0.5, 0.5),   # 0: WRIST
            (0.4, 0.4),   # 1: THUMB_CMC
            (0.3, 0.3),   # 2: THUMB_MCP
            (0.2, 0.2),   # 3: THUMB_IP
            (0.1, 0.1),   # 4: THUMB_TIP
            (0.5, 0.3),   # 5: INDEX_FINGER_MCP
            (0.5, 0.2),   # 6: INDEX_FINGER_PIP
            (0.5, 0.1),   # 7: INDEX_FINGER_DIP
            (0.5, 0.0),   # 8: INDEX_FINGER_TIP
            (0.6, 0.3),   # 9: MIDDLE_FINGER_MCP
            (0.6, 0.2),   # 10: MIDDLE_FINGER_PIP
            (0.6, 0.1),   # 11: MIDDLE_FINGER_DIP
            (0.6, 0.0),   # 12: MIDDLE_FINGER_TIP
            (0.7, 0.35),  # 13: RING_FINGER_MCP
            (0.7, 0.3),   # 14: RING_FINGER_PIP
            (0.7, 0.25),  # 15: RING_FINGER_DIP
            (0.7, 0.2),   # 16: RING_FINGER_TIP
            (0.8, 0.4),   # 17: PINKY_MCP
            (0.8, 0.35),  # 18: PINKY_PIP
            (0.8, 0.3),   # 19: PINKY_DIP
            (0.8, 0.25),  # 20: PINKY_TIP
        ]
        
        # 应用自定义位置
        positions = default_positions.copy()
        for key, value in kwargs.items():
            if isinstance(key, int) and 0 <= key < 21:
                positions[key] = value
        
        return MockHandLandmarks(positions)
    
    print("测试不同手势场景:")
    
    # 测试1: 捏合手势（拇指靠近食指）
    print("\n1. 测试捏合手势:")
    pinch_hand = create_mock_hand(
        4=(0.45, 0.15),  # 拇指尖靠近食指尖
        8=(0.5, 0.1)     # 食指尖
    )
    result = recognizer.recognize_gesture(pinch_hand)
    print(f"   识别结果: {result}")
    
    # 测试2: 握拳手势（所有手指弯曲）
    print("\n2. 测试握拳手势:")
    fist_hand = create_mock_hand(
        8=(0.5, 0.45),   # 食指尖靠近手腕
        12=(0.6, 0.45),  # 中指尖靠近手腕
        16=(0.7, 0.45),  # 无名指尖靠近手腕
        20=(0.8, 0.45),  # 小指尖靠近手腕
        4=(0.45, 0.45)   # 拇指尖靠近手腕
    )
    result = recognizer.recognize_gesture(fist_hand)
    print(f"   识别结果: {result}")
    
    # 测试3: V字手势（食指和中指伸直）
    print("\n3. 测试V字手势:")
    victory_hand = create_mock_hand(
        8=(0.5, 0.0),    # 食指伸直
        12=(0.6, 0.0),   # 中指伸直
        16=(0.7, 0.4),   # 无名指弯曲
        20=(0.8, 0.45),  # 小指弯曲
    )
    result = recognizer.recognize_gesture(victory_hand)
    print(f"   识别结果: {result}")
    
    # 测试4: OK手势（拇指和食指接近）
    print("\n4. 测试OK手势:")
    ok_hand = create_mock_hand(
        4=(0.48, 0.12),  # 拇指尖非常接近食指尖
        8=(0.5, 0.1)     # 食指尖
    )
    result = recognizer.recognize_gesture(ok_hand)
    print(f"   识别结果: {result}")
    
    # 测试5: 张开手掌（默认姿势）
    print("\n5. 测试张开手掌:")
    open_hand = create_mock_hand()  # 使用默认姿势
    result = recognizer.recognize_gesture(open_hand)
    print(f"   识别结果: {result}")
    
    print("\n=== 阈值敏感性测试 ===")
    
    # 测试不同阈值下的识别结果
    test_distances = [0.03, 0.06, 0.09, 0.12, 0.15]
    print("捏合距离测试:")
    for distance in test_distances:
        test_hand = create_mock_hand(
            4=(0.5 - distance/2, 0.1),
            8=(0.5 + distance/2, 0.1)
        )
        result = recognizer.recognize_gesture(test_hand)
        print(f"   距离 {distance:.2f}: {result}")

if __name__ == "__main__":
    test_improved_recognizer()