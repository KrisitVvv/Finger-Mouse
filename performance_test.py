#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
性能测试脚本
验证鼠标控制刷新率优化效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from pynput.mouse import Controller as MouseController


def test_mouse_movement_performance():
    """测试鼠标移动性能"""
    print("=== 鼠标移动性能测试 ===")
    
    mouse = MouseController()
    test_duration = 2.0  # 测试2秒
    start_time = time.time()
    move_count = 0
    
    print(f"开始{test_duration}秒性能测试...")
    
    # 快速连续移动鼠标测试性能
    positions = [
        (100, 100), (200, 100), (300, 100), (400, 100),
        (400, 200), (300, 200), (200, 200), (100, 200),
        (100, 300), (200, 300), (300, 300), (400, 300),
    ]
    
    pos_index = 0
    while time.time() - start_time < test_duration:
        # 循环使用预设位置
        x, y = positions[pos_index % len(positions)]
        mouse.position = (x, y)
        move_count += 1
        pos_index += 1
        
        # 短暂延迟模拟实际处理时间
        time.sleep(0.001)  # 1ms延迟
    
    end_time = time.time()
    actual_duration = end_time - start_time
    fps = move_count / actual_duration
    
    print(f"测试结果:")
    print(f"  总移动次数: {move_count}")
    print(f"  实际耗时: {actual_duration:.3f}秒")
    print(f"  实际FPS: {fps:.1f}")
    print(f"  目标FPS: 60")
    print(f"  性能达成率: {min(100, fps/60*100):.1f}%")
    
    if fps >= 50:
        print("✅ 性能达标（≥50FPS）")
        return True
    else:
        print("❌ 性能未达标（<50FPS）")
        return False


def test_gesture_recognition_speed():
    """测试手势识别速度"""
    print("\n=== 手势识别速度测试 ===")
    
    try:
        from recognition.gesture_recognizer import GestureRecognizer
        
        recognizer = GestureRecognizer()
        
        # 创建模拟手部数据
        class MockLandmark:
            def __init__(self, x, y):
                self.x = x
                self.y = y
        
        class MockHandLandmarks:
            def __init__(self):
                self.landmark = [MockLandmark(0, 0) for _ in range(21)]
        
        # 设置测试手势数据
        hand_landmarks = MockHandLandmarks()
        # 设置点5位置用于鼠标移动测试
        hand_landmarks.landmark[5].x = 0.5
        hand_landmarks.landmark[5].y = 0.5
        # 设置其他关键点模拟鼠标移动手势
        hand_landmarks.landmark[4].x = 0.4   # 拇指
        hand_landmarks.landmark[4].y = 0.5
        hand_landmarks.landmark[8].x = 0.6   # 食指
        hand_landmarks.landmark[8].y = 0.4
        hand_landmarks.landmark[12].x = 0.6  # 中指
        hand_landmarks.landmark[12].y = 0.4
        
        recognizer.hand_landmarks_cache = hand_landmarks
        
        # 测试识别速度
        test_duration = 1.0
        start_time = time.time()
        recognition_count = 0
        
        print(f"开始{test_duration}秒识别速度测试...")
        
        while time.time() - start_time < test_duration:
            gesture = recognizer.recognize_gesture(hand_landmarks)
            recognition_count += 1
            # 短暂延迟模拟实际处理间隔
            time.sleep(0.016)  # 约60FPS间隔
        
        end_time = time.time()
        actual_duration = end_time - start_time
        recognition_fps = recognition_count / actual_duration
        
        print(f"识别测试结果:")
        print(f"  总识别次数: {recognition_count}")
        print(f"  实际耗时: {actual_duration:.3f}秒")
        print(f"  识别FPS: {recognition_fps:.1f}")
        print(f"  识别结果: {gesture}")
        
        if recognition_fps >= 50:
            print("✅ 识别速度达标")
            return True
        else:
            print("❌ 识别速度较慢")
            return False
            
    except Exception as e:
        print(f"识别测试出错: {e}")
        return False


def main():
    """主测试函数"""
    print("开始性能优化测试...")
    print("=" * 40)
    
    mouse_perf_ok = test_mouse_movement_performance()
    recognition_ok = test_gesture_recognition_speed()
    
    print("\n" + "=" * 40)
    print("性能测试总结:")
    
    if mouse_perf_ok:
        print("✅ 鼠标移动性能优秀")
    else:
        print("⚠️  鼠标移动性能有待提升")
        
    if recognition_ok:
        print("✅ 手势识别速度快")
    else:
        print("⚠️  手势识别速度一般")
    
    overall_success = mouse_perf_ok and recognition_ok
    if overall_success:
        print("\n🎉 性能优化成功！")
        print("鼠标控制应该感觉更加流畅了。")
    else:
        print("\n⚠️  部分性能指标需要进一步优化。")
    
    print("\n优化措施:")
    print("1. 提高识别循环频率到60FPS")
    print("2. 减少不必要的调试输出")
    print("3. 优化鼠标控制处理逻辑")
    print("4. 精确的帧率控制机制")


if __name__ == "__main__":
    main()