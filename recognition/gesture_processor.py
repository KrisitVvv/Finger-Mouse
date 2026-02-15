#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import List, Tuple

class GestureProcessor:
    def __init__(self):
        self.frame_buffer: List[Tuple[float, float]] = []
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.smoothing_factor = 0.3
        self.gesture_stability_time = 0.3
        self.last_gesture_time = time.time()
        self.current_gesture = "无"
        
    def smooth_coordinates(self, x: float, y: float) -> Tuple[float, float]:
        if not self.frame_buffer:
            self.frame_buffer = [(x, y)] * 5 
        self.frame_buffer.append((x, y))
        if len(self.frame_buffer) > 5:
            self.frame_buffer.pop(0)
        avg_x = sum(pos[0] for pos in self.frame_buffer) / len(self.frame_buffer)
        avg_y = sum(pos[1] for pos in self.frame_buffer) / len(self.frame_buffer)
        smooth_x = self.last_mouse_x * (1 - self.smoothing_factor) + avg_x * self.smoothing_factor
        smooth_y = self.last_mouse_y * (1 - self.smoothing_factor) + avg_y * self.smoothing_factor
        
        self.last_mouse_x, self.last_mouse_y = smooth_x, smooth_y
        return smooth_x, smooth_y
    
    def stabilize_gesture(self, gesture: str) -> str:
        current_time = time.time()
        
        if gesture != self.current_gesture:
            self.current_gesture = gesture
            self.last_gesture_time = current_time
            return "无"
        else:
            if current_time - self.last_gesture_time >= self.gesture_stability_time:
                return gesture
            else:
                return "无"
    
    def get_hand_center(self, hand_landmarks: any) -> Tuple[float, float]:
        try:
            x_sum, y_sum = 0, 0
            for lm in hand_landmarks.landmark:
                x_sum += lm.x
                y_sum += lm.y
            return x_sum/21, y_sum/21
        except Exception:
            return 0.5, 0.5
    
    def update_smoothing_factor(self, factor: float):
        self.smoothing_factor = max(0.1, min(0.9, factor))
    def update_stability_time(self, stability_time: float):
        self.gesture_stability_time = max(0.1, min(1.0, stability_time))
    
    def reset_state(self):
        self.frame_buffer.clear()
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.current_gesture = "无"
        self.last_gesture_time = time.time()