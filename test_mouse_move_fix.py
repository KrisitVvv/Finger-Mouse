#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
鼠标移动手势修复测试脚本
验证仅食指中指伸出并靠拢即可触发鼠标移动的逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recognition.gesture_recognizer import GestureRecognizer
import math

def test_mouse_move_gesture():
    """测试鼠标移动手势识别"""
    print("=== 鼠标移动手势测试 ===")
    
    # 创建手势识别器
    recognizer = GestureRecognizer()
    
    # 查看当前阈值设置
    thresholds = recognizer.get_thresholds()
    print(f"当前阈值设置: {thresholds}")
    
    # 模拟手部关键点数据
    class MockHandLandmarks:
        def __init__(self):
            self.landmark = []
            # 初始化21个关键点
            for i in range(21):
                class Point:
                    def __init__(self, x, y, z):
                        self.x, self.y, self.z = x, y, z
                self.landmark.append(Point(0, 0, 0))
    
    print("\n--- 测试1: 仅食指中指伸出并靠拢 ---")
    hand_landmarks1 = MockHandLandmarks()
    
    # 设置拇指位置（远离食指关节）
    hand_landmarks1.landmark[4].x = 0.2   # 拇指尖
    hand_landmarks1.landmark[4].y = 0.5
    
    # 食指和中指伸直并靠拢
    hand_landmarks1.landmark[8].x = 0.4   # 食指尖
    hand_landmarks1.landmark[8].y = 0.3
    hand_landmarks1.landmark[12].x = 0.41  # 中指尖（很接近）
    hand_landmarks1.landmark[12].y = 0.31
    
    # 食指关节位置
    hand_landmarks1.landmark[7].x = 0.35  # 食指DIP关节
    hand_landmarks1.landmark[7].y = 0.4
    hand_landmarks1.landmark[6].x = 0.3   # 食指PIP关节
    hand_landmarks1.landmark[6].y = 0.5
    
    # 其他手指弯曲（握拳状态）
    hand_landmarks1.landmark[16].x = 0.4   # 无名指尖（靠近手掌）
    hand_landmarks1.landmark[16].y = 0.6
    hand_landmarks1.landmark[20].x = 0.45  # 小指尖（靠近手掌）
    hand_landmarks1.landmark[20].y = 0.65
    
    # 手腕位置
    hand_landmarks1.landmark[0].x = 0.4
    hand_landmarks1.landmark[0].y = 0.7
    
    # 连续识别多次测试稳定性
    print("连续识别测试:")
    mouse_move_count = 0
    for i in range(5):
        gesture = recognizer.recognize_gesture(hand_landmarks1)
        print(f"第{i+1}次识别: {gesture}")
        if gesture == "鼠标移动":
            mouse_move_count += 1
    
    print(f"识别为鼠标移动的次数: {mouse_move_count}/5")
    
    print("\n--- 测试2: 四指都伸直的情况 ---")
    hand_landmarks2 = MockHandLandmarks()
    
    # 设置拇指位置
    hand_landmarks2.landmark[4].x = 0.2   # 拇指尖
    hand_landmarks2.landmark[4].y = 0.5
    
    # 食指和中指伸直并靠拢
    hand_landmarks2.landmark[8].x = 0.4   # 食指尖
    hand_landmarks2.landmark[8].y = 0.3
    hand_landmarks2.landmark[12].x = 0.41  # 中指尖（很接近）
    hand_landmarks2.landmark[12].y = 0.31
    
    # 食指关节位置
    hand_landmarks2.landmark[7].x = 0.35  # 食指DIP关节
    hand_landmarks2.landmark[7].y = 0.4
    hand_landmarks2.landmark[6].x = 0.3   # 食指PIP关节
    hand_landmarks2.landmark[6].y = 0.5
    
    # 无名指和小指也伸直
    hand_landmarks2.landmark[16].x = 0.5   # 无名指尖（伸直）
    hand_landmarks2.landmark[16].y = 0.25
    hand_landmarks2.landmark[20].x = 0.6   # 小指尖（伸直）
    hand_landmarks2.landmark[20].y = 0.28
    
    # 手腕位置
    hand_landmarks2.landmark[0].x = 0.4
    hand_landmarks2.landmark[0].y = 0.7
    
    gesture2 = recognizer.recognize_gesture(hand_landmarks2)
    print(f"手势2识别结果: {gesture2}")
    
    print("\n--- 测试3: 食指中指不靠拢的情况 ---")
    hand_landmarks3 = MockHandLandmarks()
    
    # 设置拇指位置
    hand_landmarks3.landmark[4].x = 0.2   # 拇指尖
    hand_landmarks3.landmark[4].y = 0.5
    
    # 食指和中指伸直但不靠拢
    hand_landmarks3.landmark[8].x = 0.3   # 食指尖
    hand_landmarks3.landmark[8].y = 0.3
    hand_landmarks3.landmark[12].x = 0.6   # 中指尖（距离较远）
    hand_landmarks3.landmark[12].y = 0.3
    
    # 食指关节位置
    hand_landmarks3.landmark[7].x = 0.25  # 食指DIP关节
    hand_landmarks3.landmark[7].y = 0.4
    hand_landmarks3.landmark[6].x = 0.2   # 食指PIP关节
    hand_landmarks3.landmark[6].y = 0.5
    
    # 其他手指弯曲
    hand_landmarks3.landmark[16].x = 0.4   # 无名指尖
    hand_landmarks3.landmark[16].y = 0.6
    hand_landmarks3.landmark[20].x = 0.5   # 小指尖
    hand_landmarks3.landmark[20].y = 0.65
    
    # 手腕位置
    hand_landmarks3.landmark[0].x = 0.4
    hand_landmarks3.landmark[0].y = 0.7
    
    gesture3 = recognizer.recognize_gesture(hand_landmarks3)
    print(f"手势3识别结果: {gesture3}")
    
    # 验证结果
    success = True
    if mouse_move_count < 3:  # 至少3次识别为鼠标移动才算通过
        print("❌ 测试1失败：仅食指中指伸出并靠拢未稳定识别为鼠标移动")
        success = False
    else:
        print("✅ 测试1通过：仅食指中指伸出并靠拢能稳定识别为鼠标移动")
    
    if gesture2 != "鼠标移动":
        print("❌ 测试2失败：四指都伸直未识别为鼠标移动")
        success = False
    else:
        print("✅ 测试2通过：四指都伸直也能识别为鼠标移动")
    
    if gesture3 == "鼠标移动":
        print("❌ 测试3失败：食指中指不靠拢仍被识别为鼠标移动")
        success = False
    else:
        print("✅ 测试3通过：食指中指不靠拢不触发鼠标移动")
    
    return success

def main():
    """主测试函数"""
    print("开始测试鼠标移动手势修复...")
    
    if test_mouse_move_gesture():
        print("\n🎉 所有测试通过！鼠标移动手势修复成功")
        return True
    else:
        print("\n❌ 部分测试失败，请检查实现")
        return False

if __name__ == "__main__":
    main()