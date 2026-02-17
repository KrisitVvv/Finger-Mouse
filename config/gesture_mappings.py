# -*- coding: utf-8 -*-
from enum import Enum
from typing import Dict, List, Callable, Any
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController


class GestureAction(Enum):
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
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.default_mappings = {
            "鼠标移动": {
                "action": GestureAction.MOUSE_MOVE,
                "params": {
                    "scale": 2.5,
                    "smoothing": 0.4,
                    "use_wrist": True
                },
                "description": "移动控制鼠标移动"
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
            
            "握拳": {
                "action": GestureAction.MOUSE_DRAG_END,
                "params": {"stop_control": True}, 
                "description": "释放鼠标按键并停止控制"
            },
            "回到桌面": {
                "action": GestureAction.KEYBOARD_SHORTCUT,
                "params": {"keys": [Key.cmd, 'd']},
                "description": "Win+D回到桌面"
            },
            
            "双指捏合": {
                "action": GestureAction.MOUSE_DOUBLE_CLICK,
                "params": {"cooldown": 0.3},
                "description": "快速两次捏合执行双击"
            },
            
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
        
        self.active_mappings = self.default_mappings.copy()
        self.gesture_history: List[str] = []
        self.history_max_length = 10
        self.last_action_times: Dict[str, float] = {}
        self.control_enabled = True
        self.last_control_disable_time = 0
        self.control_resume_delay = 0.5
        
    def execute_gesture_action(self, gesture_name: str, additional_data: Any = None) -> bool:
        if gesture_name not in self.active_mappings:
            return False
            
        mapping = self.active_mappings[gesture_name]
        action = mapping["action"]
        params = mapping["params"]
        if gesture_name == "握拳":
            return self._execute_stop_control(params)
        
        if not self.control_enabled:
            current_time = time.time()
            if current_time - self.last_control_disable_time >= self.control_resume_delay:
                self.control_enabled = True
                print("鼠标控制已恢复")
            else:
                return False
        
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
        try:
            if self.control_enabled==True:
                self.control_enabled = False
                self.last_control_disable_time = time.time()
                self.mouse.release(Button.left)
                print("鼠标控制已停止")
                return True
            else:
                self.control_enabled = True
                self.last_control_disable_time = time.time()
                self.mouse.release(Button.left)
                return True
        except Exception as e:
            print(f"停止控制执行出错: {e}")
            return False
    
    def _check_cooldown(self, action_key: str, cooldown_time: float) -> bool:
        current_time = time.time()
        last_time = self.last_action_times.get(action_key, 0)
        
        if current_time - last_time >= cooldown_time:
            self.last_action_times[action_key] = current_time
            return True
        return False
    
    def _execute_mouse_move(self, hand_center: tuple, params: dict) -> bool:
        if not hand_center or not self.control_enabled:
            return False
            
        try:
            point5_x, point5_y = hand_center
            screen_width, screen_height = 1920, 1080  # TODO:
            screen_x = int(point5_x * screen_width)
            screen_y = int(point5_y * screen_height)
            
            screen_x = max(0, min(screen_width, screen_x))
            screen_y = max(0, min(screen_height, screen_y))
            
            self.mouse.position = (screen_x, screen_y)
            
            print(f"点9映射移动: ({point5_x:.3f}, {point5_y:.3f}) → 屏幕({screen_x}, {screen_y})")
            return True
            
        except Exception as e:
            print(f"鼠标移动执行出错: {e}")
            return False
    
    def _execute_mouse_click(self, button: Button, params: dict) -> bool:
        try:
            self.mouse.click(button, 1)
            print(f"执行鼠标{'左' if button == Button.left else '右'}键点击")
            return True
        except Exception as e:
            print(f"鼠标点击执行出错: {e}")
            return False
    
    def _execute_mouse_double_click(self, params: dict) -> bool:
        try:
            self.mouse.click(Button.left, 2)
            print("执行鼠标双击")
            return True
        except Exception as e:
            print(f"鼠标双击执行出错: {e}")
            return False
    
    def _execute_mouse_scroll(self, direction: int, params: dict) -> bool:
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
        try:
            if hand_center and self.control_enabled:
                self._execute_mouse_move(hand_center, {"scale": 1.0, "smoothing": 1.0})
            
            self.mouse.press(Button.left)
            print("开始鼠标拖拽")
            return True
        except Exception as e:
            print(f"开始拖拽执行出错: {e}")
            return False
    
    def _execute_mouse_drag_end(self, params: dict) -> bool:
        try:
            self.mouse.release(Button.left)
            print("结束鼠标拖拽")
            return True
        except Exception as e:
            print(f"结束拖拽执行出错: {e}")
            return False
    
    def _execute_keyboard_shortcut(self, params: dict) -> bool:
        try:
            keys = params.get("keys", [])
            if not keys:
                return False
            for key in keys:
                self.keyboard.press(key)
            for key in reversed(keys):
                self.keyboard.release(key)
                
            print(f"执行键盘快捷键: {keys}")
            return True
        except Exception as e:
            print(f"键盘快捷键执行出错: {e}")
            return False
    
    def _execute_custom_action(self, params: dict) -> bool:
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
        self.active_mappings[gesture_name] = new_mapping
    
    def add_custom_mapping(self, gesture_name: str, action: GestureAction, 
                          params: dict, description: str):
        self.active_mappings[gesture_name] = {
            "action": action,
            "params": params,
            "description": description
        }
    
    def remove_mapping(self, gesture_name: str):
        if gesture_name in self.active_mappings:
            del self.active_mappings[gesture_name]
    
    def get_available_gestures(self) -> List[str]:
        return list(self.active_mappings.keys())
    
    def get_gesture_description(self, gesture_name: str) -> str:
        if gesture_name in self.active_mappings:
            return self.active_mappings[gesture_name]["description"]
        return "未知手势"
    
    def add_to_history(self, gesture_name: str):
        self.gesture_history.append(gesture_name)
        if len(self.gesture_history) > self.history_max_length:
            self.gesture_history.pop(0)
    
    def get_recent_gestures(self, count: int = 5) -> List[str]:
        return self.gesture_history[-count:] if self.gesture_history else []
    
    def is_control_enabled(self) -> bool:
        return self.control_enabled

gesture_mapper = GestureMapping()