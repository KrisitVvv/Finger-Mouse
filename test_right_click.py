#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
鼠标右键功能测试脚本
验证拇指和中指触碰手势识别和鼠标右键控制功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recognition.gesture_recognizer import GestureRecognizer
from control.mouse_controller import MouseController
import math

def test_right_click_gesture():
    """测试鼠标右键手势识别"""
    print("=== 鼠标右键手势测试 ===")
    
    # 创建手势识别器
    recognizer = GestureRecognizer()
    
    # 查看当前阈值设置
    thresholds = recognizer.get_thresholds()
    print(f"当前阈值设置: {thresholds}")
    
    # 模拟手部关键点数据（简化版）
    class MockHandLandmarks:
        def __init__(self):
            self.landmark = []
            # 初始化21个关键点
            for i in range(21):
                class Point:
                    def __init__(self, x, y, z):
                        self.x, self.y, self.z = x, y, z
                self.landmark.append(Point(0, 0, 0))
    
    # 设置拇指和中指指尖非常接近的位置（模拟触碰）
    hand_landmarks = MockHandLandmarks()
    hand_landmarks.landmark[4].x = 0.5    # 拇指尖 x
    hand_landmarks.landmark[4].y = 0.5    # 拇指尖 y
    hand_landmarks.landmark[12].x = 0.501 # 中指尖 x（极接近）
    hand_landmarks.landmark[12].y = 0.501 # 中指尖 y（极接近）
    
    # 计算实际距离进行验证
    thumb_x, thumb_y = hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y
    middle_x, middle_y = hand_landmarks.landmark[12].x, hand_landmarks.landmark[12].y
    actual_distance = math.sqrt((thumb_x - middle_x)**2 + (thumb_y - middle_y)**2)
    print(f"拇指中指实际距离: {actual_distance:.6f}")
    print(f"点击接触阈值: {thresholds['click_contact']}")
    print(f"距离是否小于阈值: {actual_distance < thresholds['click_contact']}")
    
    # 其他手指设置为伸直状态
    # 食指尖（稍微远离确保不触发其他手势）
    hand_landmarks.landmark[8].x = 0.3
    hand_landmarks.landmark[8].y = 0.3
    # 无名指尖
    hand_landmarks.landmark[16].x = 0.7
    hand_landmarks.landmark[16].y = 0.3
    # 小指尖
    hand_landmarks.landmark[20].x = 0.8
    hand_landmarks.landmark[20].y = 0.3
    # 手腕
    hand_landmarks.landmark[0].x = 0.5
    hand_landmarks.landmark[0].y = 0.8
    
    # 连续测试多次，测试稳定性机制
    print("\n连续手势识别测试:")
    successful_recognitions = 0
    for i in range(5):
        gesture = recognizer.recognize_gesture(hand_landmarks)
        print(f"第{i+1}次识别: {gesture}")
        if gesture == "鼠标右键":
            successful_recognitions += 1
    
    print(f"\n成功识别次数: {successful_recognitions}/5")
    
    # 验证是否识别为鼠标右键（至少3次成功才算通过）
    if successful_recognitions >= 3:
        print("✅ 鼠标右键手势识别成功")
        return True
    else:
        print(f"❌ 鼠标右键手势识别失败")
        return False

def test_mouse_controller():
    """测试鼠标控制器的右键功能"""
    print("\n=== 鼠标控制器测试 ===")
    
    controller = MouseController()
    
    # 测试右键处理方法是否存在
    if hasattr(controller, '_handle_mouse_right_click'):
        print("✅ 鼠标右键处理方法存在")
        
        # 测试手势处理方法是否包含右键分支
        if hasattr(controller, 'handle_gesture'):
            import inspect
            source = inspect.getsource(controller.handle_gesture)
            if '鼠标右键' in source:
                print("✅ 手势处理方法包含鼠标右键分支")
                return True
            else:
                print("❌ 手势处理方法缺少鼠标右键分支")
                return False
        else:
            print("❌ 缺少手势处理方法")
            return False
    else:
        print("❌ 缺少鼠标右键处理方法")
        return False

def main():
    """主测试函数"""
    print("开始测试鼠标右键功能...")
    
    success_count = 0
    total_tests = 2
    
    # 测试手势识别
    if test_right_click_gesture():
        success_count += 1
    
    # 测试鼠标控制器
    if test_mouse_controller():
        success_count += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过测试: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！鼠标右键功能实现正确")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        return False

if __name__ == "__main__":
    main()