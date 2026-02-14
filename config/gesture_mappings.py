# -*- coding: utf-8 -*-
"""
手势操作映射配置 - 手腕控制版本
定义各种手势对应的鼠标和键盘操作，专为手腕控制优化
"""

from enum import Enum
from typing import Dict, List, Callable, Any
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController


class GestureAction(Enum):
    """手势动作枚举"""
    MOUSE_MOVE = "mouse_move"
    MOUSE_LEFT_CLICK = "mouse_left_click"
    MOUSE_RIGHT_CLICK = "mouse_right_click"
    MOUSE_DOUBLE_CLICK = "mouse_double_click"
    MOUSE_SCROLL_UP = "mouse_scroll_up"
    MOUSE_SCROLL_DOWN = "mouse_scroll_down"
    MOUSE_DRAG_START = "mouse_drag_start"
    MOUSE_DRAG_END = "mouse_drag_end"
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    CUSTOM_ACTION = "custom_action"


class GestureMapping:
    """手势映射配置类 - 手腕控制版本"""
    
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        
        # 默认手势映射配置 - 为手腕控制优化
        self.default_mappings = {
            # 基础鼠标操作
            "鼠标移动": {
                "action": GestureAction.MOUSE_MOVE,
                "params": {
                    "scale": 2.5,      # 增加移动速度
                    "smoothing": 0.4,  # 适中的平滑度
                    "use_wrist": True  # 使用手腕坐标
                },
                "description": "手腕移动控制鼠标移动"
            },
            "鼠标点击": {
                "action": GestureAction.MOUSE_LEFT_CLICK,
                "params": {"cooldown": 0.2},
                "description": "拇指+食指触碰执行点击"
            },
            "鼠标右键": {
                "action": GestureAction.MOUSE_RIGHT_CLICK,
                "params": {"cooldown": 0.2},
                "description": "拇指+中指触碰执行右键"
            },
            "下滚轮": {
                "action": GestureAction.MOUSE_SCROLL_DOWN,
                "params": {"amount": 3, "cooldown": 0.1},
                "description": "拇指触碰食指DIP关节向下滚动"
            },
            "上滚轮": {
                "action": GestureAction.MOUSE_SCROLL_UP,
                "params": {"amount": 3, "cooldown": 0.1},
                "description": "拇指触碰食指PIP关节向上滚动"
            },
            
            # 高级操作
            "握拳": {
                "action": GestureAction.MOUSE_DRAG_END,
                "params": {"stop_control": True},  # 停止控制的特殊参数
                "description": "释放鼠标按键并停止控制"
            },
            "回到桌面": {
                "action": GestureAction.KEYBOARD_SHORTCUT,
                "params": {"keys": [Key.cmd, 'd']},
                "description": "Win+D回到桌面"
            },
            
            # 组合手势
            "双指捏合": {
                "action": GestureAction.MOUSE_DOUBLE_CLICK,
                "params": {"cooldown": 0.3},
                "description": "快速两次捏合执行双击"
            },
            
            # 自定义操作占位符
            "自定义1": {
                "action": GestureAction.CUSTOM_ACTION,
                "params": {"callback": None},
                "description": "用户自定义操作1"
            },
            "自定义2": {
                "action": GestureAction.CUSTOM_ACTION,
                "params": {"callback": None},
                "description": "用户自定义操作2"
            }
        }
        
        # 当前激活的映射
        self.active_mappings = self.default_mappings.copy()
        
        # 手势历史记录用于组合操作
        self.gesture_history: List[str] = []
        self.history_max_length = 10
        
        # 操作冷却时间管理
        self.last_action_times: Dict[str, float] = {}
        
        # 控制状态管理
        self.control_enabled = True
        self.last_control_disable_time = 0
        self.control_resume_delay = 0.5  # 0.5秒后才能重新启用控制
        
    def execute_gesture_action(self, gesture_name: str, additional_data: Any = None) -> bool:
        """执行手势对应的操作"""
        if gesture_name not in self.active_mappings:
            return False
            
        mapping = self.active_mappings[gesture_name]
        action = mapping["action"]
        params = mapping["params"]
        
        # 特殊处理握拳手势（停止控制）
        if gesture_name == "握拳":
            return self._execute_stop_control(params)
        
        # 检查控制状态
        if not self.control_enabled:
            current_time = time.time()
            if current_time - self.last_control_disable_time >= self.control_resume_delay:
                self.control_enabled = True
                print("鼠标控制已恢复")
            else:
                # 在禁用期间忽略所有操作
                return False
        
        # 检查冷却时间
        if not self._check_cooldown(action.value, params.get("cooldown", 0)):
            return False
            
        try:
            if action == GestureAction.MOUSE_MOVE:
                return self._execute_mouse_move(additional_data, params)
            elif action == GestureAction.MOUSE_LEFT_CLICK:
                return self._execute_mouse_click(Button.left, params)
            elif action == GestureAction.MOUSE_RIGHT_CLICK:
                return self._execute_mouse_click(Button.right, params)
            elif action == GestureAction.MOUSE_DOUBLE_CLICK:
                return self._execute_mouse_double_click(params)
            elif action == GestureAction.MOUSE_SCROLL_UP:
                return self._execute_mouse_scroll(1, params)
            elif action == GestureAction.MOUSE_SCROLL_DOWN:
                return self._execute_mouse_scroll(-1, params)
            elif action == GestureAction.MOUSE_DRAG_START:
                return self._execute_mouse_drag_start(additional_data, params)
            elif action == GestureAction.MOUSE_DRAG_END:
                return self._execute_mouse_drag_end(params)
            elif action == GestureAction.KEYBOARD_SHORTCUT:
                return self._execute_keyboard_shortcut(params)
            elif action == GestureAction.CUSTOM_ACTION:
                return self._execute_custom_action(params)
            else:
                return False
                
        except Exception as e:
            print(f"执行手势操作出错: {e}")
            return False
    
    def _execute_stop_control(self, params: dict) -> bool:
        """执行停止控制操作（握拳手势专用）"""
        try:
            # 禁用控制
            self.control_enabled = False
            self.last_control_disable_time = time.time()
            
            # 释放所有鼠标按键
            self.mouse.release(Button.left)
            
            print("鼠标控制已停止（握拳手势）")
            return True
        except Exception as e:
            print(f"停止控制执行出错: {e}")
            return False
    
    def _check_cooldown(self, action_key: str, cooldown_time: float) -> bool:
        """检查操作冷却时间"""
        current_time = time.time()
        last_time = self.last_action_times.get(action_key, 0)
        
        if current_time - last_time >= cooldown_time:
            self.last_action_times[action_key] = current_time
            return True
        return False
    
    def _execute_mouse_move(self, hand_center: tuple, params: dict) -> bool:
        """执行鼠标移动操作 - 使用点5坐标直接映射"""
        if not hand_center or not self.control_enabled:
            return False
            
        try:
            # 获取点5的坐标
            point5_x, point5_y = hand_center
            
            # 16:9比例直接映射到屏幕
            screen_width, screen_height = 1920, 1080  # TODO: 从配置获取
            screen_x = int(point5_x * screen_width)
            screen_y = int(point5_y * screen_height)
            
            # 限制在屏幕范围内
            screen_x = max(0, min(screen_width, screen_x))
            screen_y = max(0, min(screen_height, screen_y))
            
            # 移动鼠标
            self.mouse.position = (screen_x, screen_y)
            
            print(f"点5映射移动: ({point5_x:.3f}, {point5_y:.3f}) → 屏幕({screen_x}, {screen_y})")
            return True
            
        except Exception as e:
            print(f"鼠标移动执行出错: {e}")
            return False
    
    def _execute_mouse_click(self, button: Button, params: dict) -> bool:
        """执行鼠标点击操作"""
        try:
            # 简单点击实现（可扩展为按住检测）
            self.mouse.click(button, 1)
            print(f"执行鼠标{'左' if button == Button.left else '右'}键点击")
            return True
        except Exception as e:
            print(f"鼠标点击执行出错: {e}")
            return False
    
    def _execute_mouse_double_click(self, params: dict) -> bool:
        """执行鼠标双击操作"""
        try:
            self.mouse.click(Button.left, 2)
            print("执行鼠标双击")
            return True
        except Exception as e:
            print(f"鼠标双击执行出错: {e}")
            return False
    
    def _execute_mouse_scroll(self, direction: int, params: dict) -> bool:
        """执行鼠标滚轮操作"""
        try:
            amount = params.get("amount", 3)
            self.mouse.scroll(0, direction * amount)
            direction_str = "上" if direction > 0 else "下"
            print(f"执行鼠标滚轮{direction_str}滚动: {direction * amount}")
            return True
        except Exception as e:
            print(f"鼠标滚动执行出错: {e}")
            return False
    
    def _execute_mouse_drag_start(self, hand_center: tuple, params: dict) -> bool:
        """开始鼠标拖拽操作"""
        try:
            if hand_center and self.control_enabled:
                # 移动到起始位置
                self._execute_mouse_move(hand_center, {"scale": 1.0, "smoothing": 1.0})
            
            self.mouse.press(Button.left)
            print("开始鼠标拖拽")
            return True
        except Exception as e:
            print(f"开始拖拽执行出错: {e}")
            return False
    
    def _execute_mouse_drag_end(self, params: dict) -> bool:
        """结束鼠标拖拽操作"""
        try:
            self.mouse.release(Button.left)
            print("结束鼠标拖拽")
            return True
        except Exception as e:
            print(f"结束拖拽执行出错: {e}")
            return False
    
    def _execute_keyboard_shortcut(self, params: dict) -> bool:
        """执行键盘快捷键操作"""
        try:
            keys = params.get("keys", [])
            if not keys:
                return False
                
            # 按下所有键
            for key in keys:
                self.keyboard.press(key)
            
            # 释放所有键（逆序）
            for key in reversed(keys):
                self.keyboard.release(key)
                
            print(f"执行键盘快捷键: {keys}")
            return True
        except Exception as e:
            print(f"键盘快捷键执行出错: {e}")
            return False
    
    def _execute_custom_action(self, params: dict) -> bool:
        """执行自定义操作"""
        try:
            callback = params.get("callback")
            if callback and callable(callback):
                callback()
                return True
            return False
        except Exception as e:
            print(f"自定义操作执行出错: {e}")
            return False
    
    def update_mapping(self, gesture_name: str, new_mapping: dict):
        """更新特定手势的映射"""
        self.active_mappings[gesture_name] = new_mapping
    
    def add_custom_mapping(self, gesture_name: str, action: GestureAction, 
                          params: dict, description: str):
        """添加自定义手势映射"""
        self.active_mappings[gesture_name] = {
            "action": action,
            "params": params,
            "description": description
        }
    
    def remove_mapping(self, gesture_name: str):
        """移除手势映射"""
        if gesture_name in self.active_mappings:
            del self.active_mappings[gesture_name]
    
    def get_available_gestures(self) -> List[str]:
        """获取所有可用的手势名称"""
        return list(self.active_mappings.keys())
    
    def get_gesture_description(self, gesture_name: str) -> str:
        """获取手势描述"""
        if gesture_name in self.active_mappings:
            return self.active_mappings[gesture_name]["description"]
        return "未知手势"
    
    def add_to_history(self, gesture_name: str):
        """添加手势到历史记录"""
        self.gesture_history.append(gesture_name)
        if len(self.gesture_history) > self.history_max_length:
            self.gesture_history.pop(0)
    
    def get_recent_gestures(self, count: int = 5) -> List[str]:
        """获取最近的手势历史"""
        return self.gesture_history[-count:] if self.gesture_history else []
    
    def is_control_enabled(self) -> bool:
        """检查控制是否启用"""
        return self.control_enabled


# 全局手势映射实例
gesture_mapper = GestureMapping()