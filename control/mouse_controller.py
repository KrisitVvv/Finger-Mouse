#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
鼠标控制器类 - 手腕控制优化版本
负责将手势识别结果转换为具体的鼠标和键盘操作，专为手腕控制优化
"""

import time
from typing import Tuple, Optional
from collections import deque
from pynput.mouse import Button, Controller as MouseControllerImpl
from pynput.keyboard import Key, Controller as KeyboardControllerImpl

# 导入手势映射系统
from config.gesture_mappings import gesture_mapper, GestureAction


class MouseController:
    """鼠标控制器类 - 手腕控制优化版本"""
    
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        self.mouse = MouseControllerImpl()
        self.keyboard = KeyboardControllerImpl()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 导入手势映射器
        from config.gesture_mappings import gesture_mapper
        self.gesture_mapper = gesture_mapper
        
        # 300FPS极致优化参数
        self.smoothing_factor = 0.8  # 更高平滑度配合300FPS预测算法
        self.movement_scale = 3.5   # 稍高移动速度（300FPS下更精确）
        self.click_cooldown = 0.1   # 更快点击响应100ms
        self.scroll_sensitivity = 25
        self.history_size = 5       # 更大窗口提高300FPS响应性
        
        # 状态跟踪
        self.last_position = None
        self.is_dragging = False
        self.last_click_time = 0
        self.click_threshold = 0.015  # 300FPS下更敏感
        self.drag_threshold = 0.008   # 300FPS下更精确
        
        # 手势历史用于稳定性判断
        self.gesture_history = deque(maxlen=self.history_size)
        self.stability_threshold = 0.7  # 70%稳定性要求（300FPS下更严格）
        
        # 300FPS专用优化
        self.velocity_history = deque(maxlen=8)  # 速度历史记录
        self.acceleration_history = deque(maxlen=6)  # 加速度历史记录
        
        # 初始化其他必要状态变量
        self.control_enabled = True
        self.mouse_pressed = False
        self.click_state = "released"
        self.last_scroll_time = 0
        self.scroll_cooldown = 0.08  # 80ms滚轮冷却
        self.scroll_amount = 4
        self.last_desktop_return = 0
        self.desktop_return_cooldown = 0.8
        self.desktop_return_active = False
        self.right_click_ready = False
        self.debug_mode = False
        self.last_hand_position = (0.5, 0.5)
        self.last_gesture = ""
    
    def handle_gesture(self, gesture: str, hand_center: Tuple[float, float] = None):
        """处理手势并执行相应鼠标操作 - 性能优化版"""
        try:
            # 性能优化：直接处理常用手势，避免复杂的映射系统调用
            if gesture == "鼠标点击":
                self._handle_mouse_click_optimized()
            elif gesture == "鼠标右键":
                self._handle_mouse_right_click_optimized()
            elif gesture == "下滚轮":
                self._handle_scroll_down_optimized()
            elif gesture == "上滚轮":
                self._handle_scroll_up_optimized()
            elif gesture == "握拳":
                self._handle_fist_optimized()
            # 注意：鼠标移动在主循环中直接处理，不经过这里
            
            self.last_gesture = gesture
            
        except Exception as e:
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"鼠标控制出错: {e}")

    def _handle_mouse_click_optimized(self):
        """优化的鼠标左键点击处理"""
        current_time = time.time()
        if current_time - self.last_click_time < self.click_cooldown:
            return
            
        self.mouse.click(Button.left, 1)
        self.last_click_time = current_time
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print("鼠标左键点击")

    def _handle_mouse_right_click_optimized(self):
        """优化的鼠标右键点击处理"""
        current_time = time.time()
        if current_time - self.last_click_time < self.click_cooldown:
            return
            
        self.mouse.click(Button.right, 1)
        self.last_click_time = current_time
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print("鼠标右键点击")

    def _handle_scroll_down_optimized(self):
        """优化的下滚轮处理"""
        current_time = time.time()
        if current_time - self.last_scroll_time >= self.scroll_cooldown:
            self.mouse.scroll(0, -self.scroll_amount)
            self.last_scroll_time = current_time
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"下滚轮: {-self.scroll_amount}")

    def _handle_scroll_up_optimized(self):
        """优化的上滚轮处理"""
        current_time = time.time()
        if current_time - self.last_scroll_time >= self.scroll_cooldown:
            self.mouse.scroll(0, self.scroll_amount)
            self.last_scroll_time = current_time
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"上滚轮: {self.scroll_amount}")

    def _handle_fist_optimized(self):
        """优化的握拳处理"""
        if self.mouse_pressed:
            self.mouse.release(Button.left)
            self.mouse_pressed = False
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print("鼠标左键释放（握拳）")
    
    def _disable_control_temporarily(self):
        """临时禁用鼠标控制"""
        if self.control_enabled:
            self.control_enabled = False
            self.last_control_disable_time = time.time()
            print("鼠标控制已临时禁用（握拳手势）")
            
            # 释放所有按下的按键
            self.release_all_buttons()
    
    def _handle_mouse_right_click(self):
        """处理鼠标右键点击手势"""
        try:
            current_time = time.time()
            
            # 防止过快重复点击
            if current_time - self.last_click_time < self.click_cooldown:
                return
            
            # 执行右键点击
            self.mouse.click(Button.right, 1)
            self.last_click_time = current_time
            print("执行鼠标右键点击")
            
        except Exception as e:
            print(f"鼠标右键点击出错: {e}")
    
    def _handle_mouse_movement(self, hand_center: Tuple[float, float] = None):
        """处理鼠标移动手势 - 使用点5坐标直接映射到屏幕"""
        try:
            if hand_center is None or not self.control_enabled:
                return
            
            # 获取点5的坐标
            point5_x, point5_y = hand_center
            
            # 16:9比例直接映射到屏幕
            # MediaPipe坐标是归一化的(0-1)，需要映射到屏幕像素坐标
            screen_x = int(point5_x * self.screen_width)
            screen_y = int(point5_y * self.screen_height)
            
            # Y轴翻转处理：摄像头坐标系Y轴向下为正，屏幕坐标系Y轴向下为正
            # 但由于是直接映射，不需要额外翻转
            
            # 限制在屏幕范围内
            screen_x = max(0, min(self.screen_width, screen_x))
            screen_y = max(0, min(self.screen_height, screen_y))
            
            # 移动鼠标到指定位置
            self.mouse.position = (screen_x, screen_y)
            
            # 更新手部位置缓存
            self.last_hand_position = (point5_x, point5_y)
            
            print(f"点5鼠标移动: ({point5_x:.3f}, {point5_y:.3f}) → 屏幕({screen_x}, {screen_y})")
            
        except Exception as e:
            print(f"鼠标移动处理出错: {e}")
    
    def _handle_scroll_down(self):
        """处理下滚轮手势 - 拇指尖触碰食指DIP关节"""
        try:
            current_time = time.time()
            if current_time - self.last_scroll_time >= self.scroll_cooldown:
                self.mouse.scroll(0, -self.scroll_amount)  # 负值表示向下滚动
                self.last_scroll_time = current_time
                print(f"下滚轮: {-self.scroll_amount}")
        except Exception as e:
            print(f"下滚轮处理出错: {e}")
    
    def _handle_scroll_up(self):
        """处理上滚轮手势 - 拇指尖触碰食指PIP关节"""
        try:
            current_time = time.time()
            if current_time - self.last_scroll_time >= self.scroll_cooldown:
                self.mouse.scroll(0, self.scroll_amount)   # 正值表示向上滚动
                self.last_scroll_time = current_time
                print(f"上滚轮: {self.scroll_amount}")
        except Exception as e:
            print(f"上滚轮处理出错: {e}")
    
    def _handle_fist(self):
        """处理握拳手势 - 鼠标左键释放并停止控制"""
        try:
            if self.mouse_pressed:
                self.mouse.release(Button.left)
                self.mouse_pressed = False
                self.click_state = "released"
                print("鼠标左键释放（握拳）")
            
            # 握拳手势的特殊处理：临时禁用控制
            self._disable_control_temporarily()
            
        except Exception as e:
            print(f"握拳处理出错: {e}")
    
    def _handle_open_palm(self):
        """处理张开手掌 - 释放鼠标按键"""
        try:
            if self.mouse_pressed:
                self.mouse.release(Button.left)
                self.mouse_pressed = False
                self.click_state = "released"
                print("鼠标左键释放（手掌张开）")
        except Exception as e:
            print(f"手掌张开处理出错: {e}")
    
    def _handle_return_to_desktop(self):
        """处理回到桌面手势 - 张开手掌到握拳的过渡"""
        try:
            current_time = time.time()
            if current_time - self.last_desktop_return >= self.desktop_return_cooldown:
                # 发送Win+D组合键回到桌面
                self.keyboard.press(Key.cmd)
                self.keyboard.press('d')
                self.keyboard.release('d')
                self.keyboard.release(Key.cmd)
                
                self.last_desktop_return = current_time
                self.desktop_return_active = True
                print("执行回到桌面操作")
                
                # 重置状态
                if self.mouse_pressed:
                    self.mouse.release(Button.left)
                    self.mouse_pressed = False
                    self.click_state = "released"
        except Exception as e:
            print(f"回到桌面处理出错: {e}")
    
    def _handle_mouse_click(self):
        """处理鼠标点击手势 - 拇指和食指指尖触碰"""
        try:
            current_time = time.time()
            
            if not self.mouse_pressed and current_time - self.last_click_time >= self.click_cooldown:
                # 按下鼠标左键
                self.mouse.press(Button.left)
                self.mouse_pressed = True
                self.click_state = "pressed"
                self.last_click_time = current_time
                print("鼠标左键按下")
            elif self.mouse_pressed:
                # 释放鼠标左键
                self.mouse.release(Button.left)
                self.mouse_pressed = False
                self.click_state = "released"
                self.last_click_time = current_time
                print("鼠标左键释放")
                
        except Exception as e:
            print(f"鼠标点击处理出错: {e}")
    
    def move_mouse(self, x: float, y: float):
        """移动鼠标到指定位置"""
        try:
            # 将相对坐标转换为绝对屏幕坐标
            abs_x = int(x * self.screen_width)
            abs_y = int(y * self.screen_height)
            self.mouse.position = (abs_x, abs_y)
        except Exception as e:
            print(f"鼠标移动出错: {e}")
    
    def scroll_mouse(self, delta: int):
        """滚动鼠标滚轮"""
        try:
            self.mouse.scroll(0, int(delta * self.scroll_sensitivity))
        except Exception as e:
            print(f"鼠标滚动出错: {e}")
    
    def release_all_buttons(self):
        """释放所有按下的鼠标按键"""
        try:
            if self.mouse_pressed:
                self.mouse.release(Button.left)
                self.mouse_pressed = False
                self.click_state = "released"
            self.right_click_ready = False
            self.desktop_return_active = False
        except Exception as e:
            print(f"释放鼠标按键出错: {e}")
    
    def update_screen_size(self, width: int, height: int):
        """更新屏幕尺寸"""
        self.screen_width = width
        self.screen_height = height
        # 同时更新手势映射器中的屏幕尺寸
        self.gesture_mapper.active_mappings["鼠标移动"]["params"]["screen_width"] = width
        self.gesture_mapper.active_mappings["鼠标移动"]["params"]["screen_height"] = height
    
    def update_scroll_sensitivity(self, sensitivity: float):
        """更新滚动灵敏度"""
        self.scroll_sensitivity = sensitivity
        # 更新手势映射器中的滚动参数
        self.gesture_mapper.active_mappings["下滚轮"]["params"]["amount"] = int(3 * sensitivity)
        self.gesture_mapper.active_mappings["上滚轮"]["params"]["amount"] = int(3 * sensitivity)
    
    def get_current_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        return self.mouse.position
    
    def reset_movement_tracking(self):
        """重置鼠标移动跟踪"""
        self.last_hand_position = (0.5, 0.5)
        self.control_enabled = True  # 重置控制状态
    
    def get_gesture_history(self, count: int = 5) -> list:
        """获取最近的手势历史"""
        return self.gesture_mapper.get_recent_gestures(count)
    
    def add_custom_gesture_mapping(self, gesture_name: str, action_params: dict):
        """添加自定义手势映射"""
        self.gesture_mapper.add_custom_mapping(
            gesture_name, 
            action_params.get("action", GestureAction.CUSTOM_ACTION),
            action_params.get("params", {}),
            action_params.get("description", "自定义手势")
        )
    
    def is_control_enabled(self) -> bool:
        """检查鼠标控制是否启用"""
        return self.control_enabled


# 保持向后兼容性的函数
def create_mouse_controller():
    """创建鼠标控制器实例的工厂函数"""
    return MouseController()