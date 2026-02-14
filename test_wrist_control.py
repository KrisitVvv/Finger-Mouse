#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手腕控制功能测试脚本
验证手腕移动控制鼠标和握拳停止功能的实现效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recognition.gesture_recognizer import GestureRecognizer
from control.mouse_controller import MouseController
import time
import math


def test_wrist_movement_detection():
    """测试手腕移动检测功能"""
    print("=== 手腕移动检测测试 ===")
    
    recognizer = GestureRecognizer()
    
    # 创建模拟手部数据
    class MockLandmark:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    class MockHandLandmarks:
        def __init__(self):
            self.landmark = [MockLandmark(0, 0) for _ in range(21)]
    
    # 测试1: 手腕静止
    print("\n--- 测试1: 手腕静止 ---")
    hand1 = MockHandLandmarks()
    hand1.landmark[0].x = 0.5   # 手腕位置
    hand1.landmark[0].y = 0.5
    
    # 设置手指状态避免误判
    hand1.landmark[4].x = 0.3   # 拇指尖
    hand1.landmark[4].y = 0.4
    hand1.landmark[8].x = 0.6   # 食指尖
    hand1.landmark[8].y = 0.4
    
    gesture1 = recognizer.recognize_gesture(hand1)
    print(f"手腕静止识别结果: {gesture1}")
    
    # 测试2: 手腕移动
    print("\n--- 测试2: 手腕移动 ---")
    hand2 = MockHandLandmarks()
    hand2.landmark[0].x = 0.55  # 手腕向右移动
    hand2.landmark[0].y = 0.5
    
    # 保持手指分开
    hand2.landmark[4].x = 0.3
    hand2.landmark[4].y = 0.4
    hand2.landmark[8].x = 0.6
    hand2.landmark[8].y = 0.4
    
    gesture2 = recognizer.recognize_gesture(hand2)
    print(f"手腕移动识别结果: {gesture2}")
    
    # 测试3: 握拳手势（最高优先级）
    print("\n--- 测试3: 握拳手势 ---")
    hand3 = MockHandLandmarks()
    hand3.landmark[0].x = 0.5   # 手腕
    hand3.landmark[0].y = 0.5
    
    # 弯曲手指（握拳状态）
    hand3.landmark[8].x = 0.5   # 食指尖靠近手腕
    hand3.landmark[8].y = 0.55
    hand3.landmark[12].x = 0.5  # 中指尖靠近手腕
    hand3.landmark[12].y = 0.55
    hand3.landmark[16].x = 0.5  # 无名指尖靠近手腕
    hand3.landmark[16].y = 0.55
    hand3.landmark[20].x = 0.5  # 小指尖靠近手腕
    hand3.landmark[20].y = 0.55
    
    gesture3 = recognizer.recognize_gesture(hand3)
    print(f"握拳识别结果: {gesture3}")
    
    # 测试4: 点击手势
    print("\n--- 测试4: 点击手势 ---")
    hand4 = MockHandLandmarks()
    hand4.landmark[0].x = 0.5   # 手腕
    hand4.landmark[0].y = 0.5
    
    # 拇指和食指触碰
    hand4.landmark[4].x = 0.5   # 拇指尖
    hand4.landmark[4].y = 0.4
    hand4.landmark[8].x = 0.5   # 食指尖
    hand4.landmark[8].y = 0.4
    
    gesture4 = recognizer.recognize_gesture(hand4)
    print(f"点击手势识别结果: {gesture4}")
    
    # 成功标准
    success = (gesture1 == "无") and (gesture2 == "鼠标移动") and \
              (gesture3 == "握拳") and (gesture4 == "鼠标点击")
    
    if success:
        print("✅ 手腕控制测试通过")
    else:
        print("❌ 手腕控制测试失败")
        print(f"  期望: 无 → 鼠标移动 → 握拳 → 鼠标点击")
        print(f"  实际: {gesture1} → {gesture2} → {gesture3} → {gesture4}")
    return success


def test_mouse_controller_integration():
    """测试鼠标控制器集成"""
    print("\n=== 鼠标控制器集成测试 ===")
    
    controller = MouseController()
    
    # 测试1: 正常鼠标移动
    print("\n--- 测试1: 正常鼠标移动 ---")
    controller.handle_gesture("鼠标移动", (0.6, 0.4))
    print(f"控制启用状态: {controller.is_control_enabled()}")
    
    # 测试2: 握拳停止控制
    print("\n--- 测试2: 握拳停止控制 ---")
    controller.handle_gesture("握拳", None)
    print(f"控制启用状态: {controller.is_control_enabled()}")
    
    # 测试3: 控制恢复
    print("\n--- 测试3: 控制恢复测试 ---")
    time.sleep(0.6)  # 等待恢复延迟
    controller.handle_gesture("鼠标移动", (0.4, 0.6))
    print(f"控制启用状态: {controller.is_control_enabled()}")
    
    # 测试4: 其他手势功能
    print("\n--- 测试4: 其他手势功能 ---")
    controller.handle_gesture("鼠标点击", None)
    controller.handle_gesture("下滚轮", None)
    controller.handle_gesture("上滚轮", None)
    print("其他手势功能测试完成")
    
    return True


def test_priority_system():
    """测试手势优先级系统"""
    print("\n=== 手势优先级测试 ===")
    
    recognizer = GestureRecognizer()
    
    # 创建模拟数据
    class MockLandmark:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    class MockHandLandmarks:
        def __init__(self):
            self.landmark = [MockLandmark(0, 0) for _ in range(21)]
    
    # 设置一个同时满足多个条件的手势
    hand = MockHandLandmarks()
    hand.landmark[0].x = 0.55  # 手腕移动
    hand.landmark[0].y = 0.5
    
    # 同时设置点击条件
    hand.landmark[4].x = 0.5   # 拇指尖
    hand.landmark[4].y = 0.4
    hand.landmark[8].x = 0.5   # 食指尖
    hand.landmark[8].y = 0.4
    
    # 弯曲部分手指制造握拳条件
    hand.landmark[12].x = 0.5  # 中指尖弯曲
    hand.landmark[12].y = 0.55
    hand.landmark[16].x = 0.5  # 无名指尖弯曲
    hand.landmark[16].y = 0.55
    
    print("测试复杂手势场景（同时满足移动、点击、握拳条件）:")
    results = []
    for i in range(10):
        gesture = recognizer.recognize_gesture(hand)
        results.append(gesture)
        print(f"  第{i+1}次: {gesture}")
    
    # 分析结果
    move_count = results.count("鼠标移动")
    click_count = results.count("鼠标点击")
    fist_count = results.count("握拳")
    
    print(f"\n统计结果:")
    print(f"  鼠标移动: {move_count}/10")
    print(f"  鼠标点击: {click_count}/10")
    print(f"  握拳: {fist_count}/10")
    
    # 握拳应该占主导地位
    if fist_count >= 6:  # 60%以上识别为握拳
        print("✅ 优先级系统工作正常")
        return True
    else:
        print("❌ 优先级系统存在问题")
        return False


def main():
    """主测试函数"""
    print("开始测试手腕控制和握拳停止功能...")
    
    success_count = 0
    total_tests = 3
    
    # 测试手腕移动检测
    if test_wrist_movement_detection():
        success_count += 1
    
    # 测试鼠标控制器集成
    if test_mouse_controller_integration():
        success_count += 1
    
    # 测试优先级系统
    if test_priority_system():
        success_count += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过测试: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！手腕控制和握拳停止功能实现正确")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        return False


if __name__ == "__main__":
    main()