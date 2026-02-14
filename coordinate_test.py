#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
坐标转换测试脚本
用于调试鼠标移动的坐标映射问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pynput.mouse import Controller
import time


def test_coordinate_mapping():
    """测试坐标映射逻辑"""
    mouse = Controller()
    
    print("=== 坐标映射测试 ===")
    print(f"当前鼠标位置: {mouse.position}")
    
    # 模拟手部坐标 (MediaPipe归一化坐标 0-1)
    test_coordinates = [
        (0.5, 0.5),   # 中心位置
        (0.6, 0.5),   # 向右
        (0.4, 0.5),   # 向左
        (0.5, 0.6),   # 向下
        (0.5, 0.4),   # 向上
    ]
    
    screen_width, screen_height = 1920, 1080
    scale = 2.5
    smoothing = 0.4
    
    print("\n测试坐标转换:")
    for i, (x, y) in enumerate(test_coordinates):
        print(f"\n测试 {i+1}: 手部坐标 ({x:.2f}, {y:.2f})")
        
        # 当前实现的转换逻辑
        flipped_y = 1.0 - y
        delta_x = (x - 0.5) * screen_width * scale
        delta_y = (flipped_y - 0.5) * screen_height * scale
        smoothed_x = delta_x * smoothing
        smoothed_y = delta_y * smoothing
        
        print(f"  翻转Y轴: {flipped_y:.2f}")
        print(f"  Delta X: {delta_x:.1f}")
        print(f"  Delta Y: {delta_y:.1f}")
        print(f"  平滑X: {smoothed_x:.1f}")
        print(f"  平滑Y: {smoothed_y:.1f}")
        
        # 计算绝对位置
        current_pos = mouse.position
        new_x = max(0, min(screen_width, current_pos[0] + int(smoothed_x)))
        new_y = max(0, min(screen_height, current_pos[1] + int(smoothed_y)))
        
        print(f"  新位置: ({new_x}, {new_y})")


def test_relative_movement():
    """测试相对移动方式"""
    mouse = Controller()
    
    print("\n\n=== 相对移动测试 ===")
    print(f"初始位置: {mouse.position}")
    
    # 模拟连续的手腕移动
    wrist_positions = [
        (0.5, 0.5),   # 起始位置
        (0.52, 0.5),  # 向右移动
        (0.54, 0.5),  # 继续向右
        (0.54, 0.48), # 向上移动
        (0.54, 0.46), # 继续向上
    ]
    
    last_pos = (0.5, 0.5)
    screen_width, screen_height = 1920, 1080
    movement_scale = 2.5
    smoothing_factor = 0.4
    
    for i, (current_x, current_y) in enumerate(wrist_positions):
        print(f"\n步骤 {i+1}: 从 {last_pos} 移动到 ({current_x:.2f}, {current_y:.2f})")
        
        # 计算相对移动量
        delta_x = (current_x - last_pos[0]) * screen_width * movement_scale
        delta_y = (current_y - last_pos[1]) * screen_height * movement_scale
        
        # Y轴翻转处理
        flipped_delta_y = -delta_y  # 手向上=Y减小，鼠标应该向上=Y减小
        
        # 应用平滑
        smooth_x = delta_x * smoothing_factor
        smooth_y = flipped_delta_y * smoothing_factor
        
        print(f"  原始Delta: X={delta_x:.1f}, Y={delta_y:.1f}")
        print(f"  翻转后Y: {flipped_delta_y:.1f}")
        print(f"  平滑后: X={smooth_x:.1f}, Y={smooth_y:.1f}")
        
        # 获取当前鼠标位置
        current_mouse_x, current_mouse_y = mouse.position
        
        # 计算新位置
        new_x = max(0, min(screen_width, current_mouse_x + int(smooth_x)))
        new_y = max(0, min(screen_height, current_mouse_y + int(smooth_y)))
        
        print(f"  鼠标移动: ({current_mouse_x}, {current_mouse_y}) → ({new_x}, {new_y})")
        
        # 更新位置
        last_pos = (current_x, current_y)


if __name__ == "__main__":
    test_coordinate_mapping()
    test_relative_movement()