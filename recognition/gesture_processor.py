#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手势处理器类
负责手势的平滑处理和状态管理
"""

import time
from typing import List, Tuple


class GestureProcessor:
    """手势处理器类"""
    
    def __init__(self):
        self.frame_buffer: List[Tuple[float, float]] = []
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.smoothing_factor = 0.3
        self.gesture_stability_time = 0.3  # 手势稳定时间（秒）
        self.last_gesture_time = time.time()
        self.current_gesture = "无"
        
    def smooth_coordinates(self, x: float, y: float) -> Tuple[float, float]:
        """平滑坐标值"""
        if not self.frame_buffer:
            self.frame_buffer = [(x, y)] * 5  # 初始化缓冲区
        
        # 添加新坐标到缓冲区
        self.frame_buffer.append((x, y))
        if len(self.frame_buffer) > 5:
            self.frame_buffer.pop(0)
        
        # 计算平均值
        avg_x = sum(pos[0] for pos in self.frame_buffer) / len(self.frame_buffer)
        avg_y = sum(pos[1] for pos in self.frame_buffer) / len(self.frame_buffer)
        
        # 应用平滑因子
        smooth_x = self.last_mouse_x * (1 - self.smoothing_factor) + avg_x * self.smoothing_factor
        smooth_y = self.last_mouse_y * (1 - self.smoothing_factor) + avg_y * self.smoothing_factor
        
        self.last_mouse_x, self.last_mouse_y = smooth_x, smooth_y
        return smooth_x, smooth_y
    
    def stabilize_gesture(self, gesture: str) -> str:
        """手势稳定化处理"""
        current_time = time.time()
        
        if gesture != self.current_gesture:
            # 手势发生变化，重置计时器
            self.current_gesture = gesture
            self.last_gesture_time = current_time
            return "无"  # 返回"无"表示手势还在变化中
        else:
            # 手势保持不变，检查是否达到稳定时间
            if current_time - self.last_gesture_time >= self.gesture_stability_time:
                return gesture
            else:
                return "无"
    
    def get_hand_center(self, hand_landmarks: any) -> Tuple[float, float]:
        """计算手部中心坐标"""
        try:
            x_sum, y_sum = 0, 0
            for lm in hand_landmarks.landmark:
                x_sum += lm.x
                y_sum += lm.y
            return x_sum/21, y_sum/21
        except Exception:
            return 0.5, 0.5
    
    def update_smoothing_factor(self, factor: float):
        """更新平滑因子"""
        self.smoothing_factor = max(0.1, min(0.9, factor))
    
    def update_stability_time(self, stability_time: float):
        """更新手势稳定时间"""
        self.gesture_stability_time = max(0.1, min(1.0, stability_time))
    
    def reset_state(self):
        """重置处理器状态"""
        self.frame_buffer.clear()
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.current_gesture = "无"
        self.last_gesture_time = time.time()