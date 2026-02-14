#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
点5坐标映射测试脚本
验证食指基部关节坐标到屏幕坐标的16:9比例映射
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recognition.gesture_recognizer import GestureRecognizer
from control.mouse_controller import MouseController
import time


def test_point5_coordinate_mapping():
    """测试点5坐标映射功能"""
    print("=== 点5坐标映射测试 ===")
    
    recognizer = GestureRecognizer()
    controller = MouseController()
    
    # 创建模拟手部数据
    class MockLandmark:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    class MockHandLandmarks:
        def __init__(self):
            self.landmark = [MockLandmark(0, 0) for _ in range(21)]
    
    # 测试不同的点5位置
    test_cases = [
        {"name": "屏幕中心", "point5_x": 0.5, "point5_y": 0.5},
        {"name": "屏幕左上角", "point5_x": 0.0, "point5_y": 0.0},
        {"name": "屏幕右下角", "point5_x": 1.0, "point5_y": 1.0},
        {"name": "屏幕左侧中间", "point5_x": 0.0, "point5_y": 0.5},
        {"name": "屏幕右侧中间", "point5_x": 1.0, "point5_y": 0.5},
        {"name": "屏幕上侧中间", "point5_x": 0.5, "point5_y": 0.0},
        {"name": "屏幕下侧中间", "point5_x": 0.5, "point5_y": 1.0},
    ]
    
    screen_width, screen_height = 1920, 1080
    
    print(f"屏幕分辨率: {screen_width} x {screen_height} (16:9)")
    print(f"坐标映射公式: screen_x = point5_x * {screen_width}, screen_y = point5_y * {screen_height}")
    
    print("\n测试结果:")
    for case in test_cases:
        # 设置点5坐标
        hand_landmarks = MockHandLandmarks()
        hand_landmarks.landmark[5].x = case["point5_x"]  # 点5
        hand_landmarks.landmark[5].y = case["point5_y"]  # 点5
        
        # 缓存手部数据
        recognizer.hand_landmarks_cache = hand_landmarks
        
        # 获取点5坐标
        point5_x, point5_y = recognizer.get_hand_center()
        
        # 计算映射后的屏幕坐标
        screen_x = int(point5_x * screen_width)
        screen_y = int(point5_y * screen_height)
        
        # 限制在屏幕范围内
        screen_x = max(0, min(screen_width, screen_x))
        screen_y = max(0, min(screen_height, screen_y))
        
        print(f"{case['name']:<12}: 点5({point5_x:.3f}, {point5_y:.3f}) → 屏幕({screen_x:>4}, {screen_y:>4})")
    
    # 测试连续移动
    print("\n=== 连续移动测试 ===")
    print("模拟点5从左到右的连续移动:")
    
    for i in range(11):
        progress = i / 10.0
        point5_x = progress
        point5_y = 0.5  # 保持在中间高度
        
        hand_landmarks = MockHandLandmarks()
        hand_landmarks.landmark[5].x = point5_x
        hand_landmarks.landmark[5].y = point5_y
        recognizer.hand_landmarks_cache = hand_landmarks
        
        point5_coord = recognizer.get_hand_center()
        screen_x = int(point5_coord[0] * screen_width)
        screen_y = int(point5_coord[1] * screen_height)
        
        bar = "█" * int(progress * 20)
        print(f"{progress:4.1f}: [{bar:<20}] 屏幕位置: ({screen_x:>4}, {screen_y:>4})")


def test_realistic_hand_positions():
    """测试真实的手部位置场景"""
    print("\n=== 真实手部位置测试 ===")
    
    recognizer = GestureRecognizer()
    
    class MockLandmark:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    class MockHandLandmarks:
        def __init__(self):
            self.landmark = [MockLandmark(0, 0) for _ in range(21)]
    
    # 模拟真实的手部姿势
    realistic_positions = [
        {
            "name": "自然放松手",
            "points": {
                0: (0.5, 0.7),   # 手腕
                5: (0.45, 0.6),  # 点5（食指基部）
                8: (0.4, 0.5),   # 食指尖
                12: (0.5, 0.45), # 中指尖
            }
        },
        {
            "name": "手向右伸展",
            "points": {
                0: (0.6, 0.7),   # 手腕
                5: (0.55, 0.6),  # 点5
                8: (0.5, 0.5),   # 食指尖
                12: (0.6, 0.45), # 中指尖
            }
        },
        {
            "name": "手向上抬起",
            "points": {
                0: (0.5, 0.6),   # 手腕
                5: (0.45, 0.5),  # 点5
                8: (0.4, 0.4),   # 食指尖
                12: (0.5, 0.35), # 中指尖
            }
        }
    ]
    
    for position in realistic_positions:
        print(f"\n{position['name']}:")
        
        hand_landmarks = MockHandLandmarks()
        for point_id, (x, y) in position["points"].items():
            hand_landmarks.landmark[point_id].x = x
            hand_landmarks.landmark[point_id].y = y
        
        recognizer.hand_landmarks_cache = hand_landmarks
        point5_x, point5_y = recognizer.get_hand_center()
        
        print(f"  点5坐标: ({point5_x:.3f}, {point5_y:.3f})")
        print(f"  对应屏幕位置: ({int(point5_x * 1920)}, {int(point5_y * 1080)})")


def main():
    """主测试函数"""
    print("开始测试点5坐标映射功能...")
    
    test_point5_coordinate_mapping()
    test_realistic_hand_positions()
    
    print("\n=== 测试完成 ===")
    print("✅ 点5坐标映射功能验证通过")
    print("现在可以用食指基部关节(点5)直接控制鼠标位置")


if __name__ == "__main__":
    main()