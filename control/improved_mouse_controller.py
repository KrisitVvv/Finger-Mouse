#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import Tuple, Optional
from collections import deque
from pynput.mouse import Button, Controller as MouseControllerImpl

class ImprovedMouseController:
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.mouse = MouseControllerImpl()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # config
        self.movement_scale = 1.8
        self.smoothing_factor = 0.7
        self.dead_zone = 0.015
        self.max_movement = 50
        
        self.last_hand_position = (0.5, 0.5)
        self.control_enabled = True
        self.debug_mode = False
        
        self.filter_alpha = 0.7
        self.filtered_position = (0.5, 0.5)
        
        self.position_history = deque(maxlen=3)
        self.velocity_history = deque(maxlen=3)
    
    def handle_mouse_movement(self, hand_center: Tuple[float, float]):
        try:
            if hand_center is None or not self.control_enabled:
                return
            current_x, current_y = hand_center
            filtered_x = self.filtered_position[0] * (1 - self.filter_alpha) + current_x * self.filter_alpha
            filtered_y = self.filtered_position[1] * (1 - self.filter_alpha) + current_y * self.filter_alpha
            self.filtered_position = (filtered_x, filtered_y)
            delta_x = abs(filtered_x - self.last_hand_position[0])
            delta_y = abs(filtered_y - self.last_hand_position[1])
            if delta_x < self.dead_zone and delta_y < self.dead_zone:
                if self.debug_mode:
                    print(f"[DEBUG] 移动量过小，忽略移动 (Δx={delta_x:.4f}, Δy={delta_y:.4f})")
                return
            rel_delta_x = (filtered_x - self.last_hand_position[0]) * self.screen_width * self.movement_scale
            rel_delta_y = (filtered_y - self.last_hand_position[1]) * self.screen_height * self.movement_scale
            smooth_delta_x = rel_delta_x * self.smoothing_factor
            smooth_delta_y = rel_delta_y * self.smoothing_factor
            smooth_delta_x = max(-self.max_movement, min(self.max_movement, smooth_delta_x))
            smooth_delta_y = max(-self.max_movement, min(self.max_movement, smooth_delta_y))
            current_mouse_x, current_mouse_y = self.mouse.position
            new_x = max(0, min(self.screen_width, current_mouse_x + int(smooth_delta_x)))
            new_y = max(0, min(self.screen_height, current_mouse_y + int(smooth_delta_y)))
            self.mouse.position = (new_x, new_y)
            self.last_hand_position = (filtered_x, filtered_y)
            self.position_history.append((filtered_x, filtered_y))
            
            if self.debug_mode:
                print(f"[DEBUG] 手部({filtered_x:.3f}, {filtered_y:.3f}) "
                      f"→ 鼠标移动({smooth_delta_x:+.1f}, {smooth_delta_y:+.1f}) px "
                      f"→ 新位置({new_x}, {new_y})")
            
        except Exception as e:
            if self.debug_mode:
                print(f"[ERROR] 鼠标移动处理出错: {e}")
    
    def update_parameters(self, movement_scale: float = None, 
                         smoothing_factor: float = None,
                         dead_zone: float = None,
                         max_movement: float = None):
        if movement_scale is not None:
            self.movement_scale = max(0.5, min(5.0, movement_scale))
        if smoothing_factor is not None:
            self.smoothing_factor = max(0.1, min(1.0, smoothing_factor))
        if dead_zone is not None:
            self.dead_zone = max(0.005, min(0.05, dead_zone))
        if max_movement is not None:
            self.max_movement = max(10, min(200, max_movement))
        
        if self.debug_mode:
            print(f"[PARAMS] Scale={self.movement_scale}, Smooth={self.smoothing_factor}, "
                  f"DeadZone={self.dead_zone}, MaxMove={self.max_movement}")
    
    def enable_debug_mode(self, enabled: bool = True):
        self.debug_mode = enabled
        if enabled:
            print("[DEBUG] 调试模式已启用")
        else:
            print("[DEBUG] 调试模式已禁用")
    
    def reset_position(self):
        self.last_hand_position = (0.5, 0.5)
        self.filtered_position = (0.5, 0.5)
        self.position_history.clear()
        self.velocity_history.clear()
        if self.debug_mode:
            print("[RESET] 位置跟踪已重置")


class AdaptiveMouseController:
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.base_controller = ImprovedMouseController(screen_width, screen_height)
        self.adaptation_enabled = True
        self.learning_window = 50
        self.movement_history = deque(maxlen=self.learning_window)
        self.sensitivity_adjustment = 1.0
        self.initial_scale = 1.8
        self.initial_smoothing = 0.7
        self.initial_dead_zone = 0.015
    
        self.base_controller.update_parameters(
            movement_scale=self.initial_scale,
            smoothing_factor=self.initial_smoothing,
            dead_zone=self.initial_dead_zone
        )
    
    def handle_mouse_movement(self, hand_center: Tuple[float, float]):
        try:
            if hand_center is not None:
                self.movement_history.append(hand_center)
                self._adapt_parameters()
            self.base_controller.handle_mouse_movement(hand_center)
            
        except Exception as e:
            if self.base_controller.debug_mode:
                print(f"[ADAPT ERROR] 自适应处理出错: {e}")
    
    def _adapt_parameters(self):
        if not self.adaptation_enabled or len(self.movement_history) < 20:
            return
        movements = list(self.movement_history)
        recent_movements = movements[-10:]
        avg_movement = 0
        for i in range(1, len(recent_movements)):
            prev_pos = recent_movements[i-1]
            curr_pos = recent_movements[i]
            delta = ((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)**0.5
            avg_movement += delta
        
        avg_movement /= (len(recent_movements) - 1)
        if avg_movement > 0.03:
            self.sensitivity_adjustment *= 0.95
        elif avg_movement < 0.005:
            self.sensitivity_adjustment *= 1.05

        self.sensitivity_adjustment = max(0.5, min(2.0, self.sensitivity_adjustment))
        adjusted_scale = self.initial_scale * self.sensitivity_adjustment
        self.base_controller.update_parameters(movement_scale=adjusted_scale)
        
        if self.base_controller.debug_mode:
            print(f"[ADAPT] 平均移动: {avg_movement:.4f}, 调整因子: {self.sensitivity_adjustment:.2f}")
    
    def update_parameters(self, **kwargs):
        self.base_controller.update_parameters(**kwargs)
    
    def enable_adaptation(self, enabled: bool = True):
        self.adaptation_enabled = enabled
        if self.base_controller.debug_mode:
            status = "启用" if enabled else "禁用"
            print(f"[ADAPT] 自适应功能已{status}")
    
    def reset_adaptation(self):
        self.movement_history.clear()
        self.sensitivity_adjustment = 1.0
        self.base_controller.update_parameters(
            movement_scale=self.initial_scale,
            smoothing_factor=self.initial_smoothing,
            dead_zone=self.initial_dead_zone
        )
        if self.base_controller.debug_mode:
            print("[ADAPT] 自适应学习已重置")