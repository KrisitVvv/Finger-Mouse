#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
改进的坐标转换测试脚本
验证修复后的鼠标移动坐标映射
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pynput.mouse import Controller
import time


def test_fixed_coordinate_mapping():
    """测试修复后的坐标映射逻辑"""
    mouse = Controller()
    
    print("=== 修复后的坐标映射测试 ===")
    print(f"当前鼠标位置: {mouse.position}")
    
    # 模拟手部坐标移动序列
    hand_movements = [
        (0.5, 0.5),   # 中心位置（起始）
        (0.55, 0.5),  # 向右移动
        (0.6, 0.5),   # 继续向右
        (0.6, 0.45),  # 向上移动
        (0.6, 0.4),   # 继续向上
        (0.55, 0.4),  # 向左移动
        (0.5, 0.4),   # 继续向左
        (0.5, 0.45),  # 向下移动
        (0.5, 0.5),   # 回到中心
    ]
    
    screen_width, screen_height = 1920, 1080
    scale = 2.5
    smoothing = 0.4
    
    last_pos = (0.5, 0.5)
    
    print("\n连续移动测试:")
    for i, (current_x, current_y) in enumerate(hand_movements):
        print(f"\n步骤 {i+1}: 从 {last_pos} → ({current_x:.2f}, {current_y:.2f})")
        
        # 计算相对移动量（修复后的逻辑）
        delta_x = (current_x - last_pos[0]) * screen_width * scale
        delta_y = (current_y - last_pos[1]) * screen_height * scale  # Y轴直接使用，不翻转
        
        # 应用平滑
        smooth_x = delta_x * smoothing
        smooth_y = delta_y * smoothing
        
        print(f"  相对移动: ΔX={delta_x:.1f}, ΔY={delta_y:.1f}")
        print(f"  平滑后: X={smooth_x:.1f}, Y={smooth_y:.1f}")
        
        # 预期的鼠标移动方向
        if smooth_x > 0:
            x_direction = "向右"
        elif smooth_x < 0:
            x_direction = "向左"
        else:
            x_direction = "不动"
            
        if smooth_y > 0:
            y_direction = "向下"
        elif smooth_y < 0:
            y_direction = "向上"
        else:
            y_direction = "不动"
            
        print(f"  预期方向: X:{x_direction}, Y:{y_direction}")
        
        # 更新位置
        last_pos = (current_x, current_y)


def test_absolute_mapping_fix():
    """测试绝对坐标映射修复"""
    mouse = Controller()
    
    print("\n\n=== 绝对坐标映射修复测试 ===")
    
    # 使用中心点作为参考
    center_x, center_y = 0.5, 0.5
    screen_width, screen_height = 1920, 1080
    scale = 2.5
    smoothing = 0.4
    
    test_points = [
        (0.5, 0.5),   # 中心
        (0.6, 0.5),   # 右侧
        (0.4, 0.5),   # 左侧
        (0.5, 0.4),   # 上方
        (0.5, 0.6),   # 下方
    ]
    
    print("相对于中心点的绝对位置映射:")
    for i, (x, y) in enumerate(test_points):
        # 相对于中心点的偏移
        offset_x = (x - center_x) * screen_width * scale
        offset_y = (y - center_y) * screen_height * scale
        
        smooth_x = offset_x * smoothing
        smooth_y = offset_y * smoothing
        
        print(f"\n点 {i+1} ({x:.1f}, {y:.1f}):")
        print(f"  相对于中心偏移: X={offset_x:.1f}, Y={offset_y:.1f}")
        print(f"  平滑后: X={smooth_x:.1f}, Y={smooth_y:.1f}")
        
        # 方向判断
        x_dir = "右" if smooth_x > 0 else ("左" if smooth_x < 0 else "中")
        y_dir = "下" if smooth_y > 0 else ("上" if smooth_y < 0 else "中")
        print(f"  移动方向: {x_dir}{y_dir}")


if __name__ == "__main__":
    test_fixed_coordinate_mapping()
    test_absolute_mapping_fix()