#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from typing import Tuple, Optional
from pynput.mouse import Button, Controller as MouseControllerImpl
from pynput.keyboard import Key, Controller as KeyboardControllerImpl
from config.gesture_mappings import gesture_mapper, GestureAction

class MouseController:
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.mouse = MouseControllerImpl()
        self.keyboard = KeyboardControllerImpl()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.control_enabled = True
        self.debug_mode = False
        self.last_click_time = 0
        self.click_cooldown = 0.15
        self.last_scroll_time = 0
        self.scroll_cooldown = 0.1
        self.scroll_amount = 3 
        self.mouse_pressed = False
        self.last_gesture = "无"
        
        self.last_hand_position = (0.5, 0.5)
        self.smoothing_factor = 0.02
        self.movement_scale = 7
        self.last_control_disable_time = 0
        self.control_resume_delay = 0.5
    
    def handle_gesture(self, gesture: str, hand_center: Tuple[float, float] = None):
        try:
            if not self.control_enabled:
                current_time = time.time()
                if current_time - self.last_control_disable_time >= self.control_resume_delay:
                    self.control_enabled = True
                    print("鼠标控制已恢复")
                else:
                    if self.debug_mode:
                        print(f"鼠标控制暂时禁用，剩余时间: {self.control_resume_delay - (current_time - self.last_control_disable_time):.2f}s")
                    return
            
            if self.debug_mode:
                print(f"[DEBUG] 处理手势: {gesture}, 控制启用: {self.control_enabled}")
            if gesture == "鼠标点击":
                self._handle_mouse_click_unified()
            elif gesture == "鼠标右键":
                self._handle_mouse_right_click_unified()
            elif gesture == "下滚轮":
                self._handle_scroll_down_unified()
            elif gesture == "上滚轮":
                self._handle_scroll_up_unified()
            elif gesture == "握拳":
                self._handle_fist_unified()
            elif gesture == "鼠标移动":
                if self.debug_mode:
                    print("[DEBUG] 鼠标移动手势接收")
            else:
                if self.debug_mode:
                    print(f"[DEBUG] 未知手势: {gesture}")
            self.last_gesture = gesture
        except Exception as e:
            print(f"鼠标控制出错: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
    
    def _handle_mouse_click_unified(self):
        try:
            current_time = time.time()
            if current_time - self.last_click_time < self.click_cooldown:
                if self.debug_mode:
                    remaining = self.click_cooldown - (current_time - self.last_click_time)
                    print(f"[DEBUG] 点击冷却中，剩余时间: {remaining:.3f}s")
                return
            self.mouse.click(Button.left, 1)
            self.last_click_time = current_time
            print("鼠标左键点击执行")
        except Exception as e:
            print(f"鼠标点击处理出错: {e}")
    
    def _handle_mouse_right_click_unified(self):
        try:
            current_time = time.time()
            if current_time - self.last_click_time < self.click_cooldown:
                return
            self.mouse.click(Button.right, 1)
            self.last_click_time = current_time
            
            print("鼠标右键点击执行")
            
        except Exception as e:
            print(f"鼠标右键处理出错: {e}")
    
    def _handle_scroll_down_unified(self):
        try:
            current_time = time.time()
            if current_time - self.last_scroll_time < self.scroll_cooldown:
                if self.debug_mode:
                    remaining = self.scroll_cooldown - (current_time - self.last_scroll_time)
                    print(f"[DEBUG] 滚动冷却中，剩余时间: {remaining:.3f}s")
                return
            self.mouse.scroll(0, -self.scroll_amount)
            self.last_scroll_time = current_time
            
            print(f"下滚轮执行: {-self.scroll_amount}")
            
        except Exception as e:
            print(f"下滚轮处理出错: {e}")
    
    def _handle_scroll_up_unified(self):
        try:
            current_time = time.time()
            if current_time - self.last_scroll_time < self.scroll_cooldown:
                return
            self.mouse.scroll(0, self.scroll_amount)
            self.last_scroll_time = current_time
            
            print(f"上滚轮执行: {self.scroll_amount}")
            
        except Exception as e:
            print(f"上滚轮处理出错: {e}")
    
    def enable_control(self):
        self.control_enabled = True
        self.last_control_disable_time = 0
        print("鼠标控制强制启用")
    
    def disable_control(self):
        self.control_enabled = False
        print("鼠标控制强制禁用")
    
    def is_control_enabled(self) -> bool:
        return self.control_enabled
    
    def get_status_info(self) -> dict:
        return {
            'control_enabled': self.control_enabled,
            'mouse_pressed': self.mouse_pressed,
            'last_gesture': self.last_gesture,
            'click_cooldown_remaining': max(0, self.click_cooldown - (time.time() - self.last_click_time)),
            'scroll_cooldown_remaining': max(0, self.scroll_cooldown - (time.time() - self.last_scroll_time))
        }
    
    def reset_state(self):
        self.control_enabled = True
        self.mouse_pressed = False
        self.last_click_time = 0
        self.last_scroll_time = 0
        self.last_control_disable_time = 0
        print("控制器状态已重置")
    
    def update_screen_size(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        print(f"屏幕尺寸已更新为: {width} x {height}")
    
    def release_all_buttons(self):
        """释放所有按下的鼠标按钮"""
        try:
            # 释放左键
            if self.mouse_pressed:
                self.mouse.release(Button.left)
                self.mouse_pressed = False
                print("释放鼠标左键")
            
            # 也可以在这里添加其他按钮的释放逻辑
            # 例如右键、中键等
            
            print("所有鼠标按钮已释放")
            
        except Exception as e:
            print(f"释放鼠标按钮时出错: {e}")

EnhancedMouseController = MouseController
HighSensitivityMouseController = MouseController