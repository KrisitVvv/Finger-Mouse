#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pynput.keyboard import Listener, Key
from typing import Callable, Optional

class KeyboardListener:
    def __init__(self, toggle_callback: Callable[[], None]):
        self.toggle_callback = toggle_callback
        self.listener: Optional[Listener] = None
        self.ctrl_pressed = False
        self.alt_pressed = False
    
    def start(self):
        try:
            self.listener = Listener(on_press=self._on_press, on_release=self._on_release)
            self.listener.start()
            print("键盘监听器已启动")
        except Exception as e:
            print(f"启动键盘监听器失败: {e}")
    
    def stop(self):
        try:
            if self.listener:
                self.listener.stop()
                print("键盘监听器已停止")
        except Exception as e:
            print(f"停止键盘监听器失败: {e}")
    
    def _on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char == 'g':
                if self.ctrl_pressed and self.alt_pressed:
                    if self.toggle_callback:
                        self.toggle_callback()
            if key in [Key.ctrl_l, Key.ctrl_r]:
                self.ctrl_pressed = True
            elif key in [Key.alt_l, Key.alt_r]:
                self.alt_pressed = True
                
        except Exception as e:
            print(f"键盘按下事件处理出错: {e}")
    
    def _on_release(self, key):
        try:
            if key in [Key.ctrl_l, Key.ctrl_r]:
                self.ctrl_pressed = False
            elif key in [Key.alt_l, Key.alt_r]:
                self.alt_pressed = False
                
        except Exception as e:
            print(f"键盘释放事件处理出错: {e}")