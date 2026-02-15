#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
from typing import Tuple, Optional
from collections import deque

from config import ConfigManager
from utils.logger import setup_logger
from recognition.hand_detector import HandDetector
from control.mouse_controller import MouseController
from control.keyboard_listener import KeyboardListener
from .controls_panel import ControlsPanel
from .preview_panel import PreviewPanel


class MainWindow:    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FingerMouse")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        self.logger = setup_logger()
        # debug mode switch
        self.debug_mode = False
        self.current_gesture = "无"
        self.previous_gesture = "无"
        self.gesture_change_time = 0
        self.gesture_stable_time = 0.1
        self.last_gesture_execution = {}
        self.config_manager = ConfigManager()
        self.config_manager.initialize_with_root(root)
        self.hand_detector = HandDetector()
        self.mouse_controller = MouseController()
        self.keyboard_listener = KeyboardListener(self._toggle_recognition)
        self.is_running = False
        self.mouse_control_enabled = False
        self.is_paused = False
        self.recognize_thread: Optional[threading.Thread] = None
        self.current_gesture = "无"
        self.config_manager.load_config()
        self._build_gui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.keyboard_listener.start()
        self._update_resolution_display()
        self.logger.info("Main Window Initialized.")
    def _build_gui(self):
        self._create_menu()
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.controls_panel = ControlsPanel(
            main_frame, 
            self.config_manager,
            self._start_recognition,
            self._stop_recognition,
            self._toggle_pause,
            self._toggle_mouse_control,
            self._update_detector
        )
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.preview_panel = PreviewPanel(right_frame, self._update_gesture_display)
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
    
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存配置", command=self._save_config)
        file_menu.add_command(label="加载配置", command=self._load_config_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_close)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="手势识别阈值", command=self._show_gesture_thresholds_dialog)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    def _show_gesture_thresholds_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("手势识别阈值设置")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()
        current_thresholds = self.hand_detector.gesture_recognizer.get_thresholds()
        ttk.Label(dialog, text="调整手势识别的敏感度阈值:", font=("Arial", 12)).pack(pady=10)
        pinch_frame = ttk.Frame(dialog)
        pinch_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(pinch_frame, text="精确触碰阈值:").pack(side=tk.LEFT)
        pinch_var = tk.DoubleVar(value=current_thresholds['pinch'])
        pinch_scale = ttk.Scale(pinch_frame, from_=0.03, to=0.12, variable=pinch_var, orient=tk.HORIZONTAL)
        pinch_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        pinch_label = ttk.Label(pinch_frame, text=f"{pinch_var.get():.3f}")
        pinch_label.pack(side=tk.LEFT)
        def update_pinch_label(val):
            pinch_label.config(text=f"{float(val):.3f}")
        pinch_scale.configure(command=update_pinch_label)
        click_frame = ttk.Frame(dialog)
        click_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(click_frame, text="点击接触阈值:").pack(side=tk.LEFT)
        click_var = tk.DoubleVar(value=current_thresholds['click_contact'])
        click_scale = ttk.Scale(click_frame, from_=0.03, to=0.08, variable=click_var, orient=tk.HORIZONTAL)
        click_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        click_label = ttk.Label(click_frame, text=f"{click_var.get():.3f}")
        click_label.pack(side=tk.LEFT)
        def update_click_label(val):
            click_label.config(text=f"{float(val):.3f}")
        click_scale.configure(command=update_click_label)
        proximity_frame = ttk.Frame(dialog)
        proximity_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(proximity_frame, text="手指靠近阈值:").pack(side=tk.LEFT)
        proximity_var = tk.DoubleVar(value=current_thresholds['finger_proximity'])
        proximity_scale = ttk.Scale(proximity_frame, from_=0.02, to=0.08, variable=proximity_var, orient=tk.HORIZONTAL)
        proximity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        proximity_label = ttk.Label(proximity_frame, text=f"{proximity_var.get():.3f}")
        proximity_label.pack(side=tk.LEFT)

        def update_proximity_label(val):
            proximity_label.config(text=f"{float(val):.3f}")
        proximity_scale.configure(command=update_proximity_label)
        fist_frame = ttk.Frame(dialog)
        fist_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(fist_frame, text="握拳阈值:").pack(side=tk.LEFT)
        fist_var = tk.DoubleVar(value=current_thresholds['fist'])
        fist_scale = ttk.Scale(fist_frame, from_=0.08, to=0.20, variable=fist_var, orient=tk.HORIZONTAL)
        fist_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        fist_label = ttk.Label(fist_frame, text=f"{fist_var.get():.3f}")
        fist_label.pack(side=tk.LEFT)

        def update_fist_label(val):
            fist_label.config(text=f"{float(val):.3f}")
        fist_scale.configure(command=update_fist_label)
        wheel_up_frame = ttk.Frame(dialog)
        wheel_up_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(wheel_up_frame, text="上滚轮阈值:").pack(side=tk.LEFT)
        wheel_up_var = tk.DoubleVar(value=current_thresholds['wheel_up_threshold'])
        wheel_up_scale = ttk.Scale(wheel_up_frame, from_=0.03, to=0.15, variable=wheel_up_var, orient=tk.HORIZONTAL)
        wheel_up_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        wheel_up_label = ttk.Label(wheel_up_frame, text=f"{wheel_up_var.get():.3f}")
        wheel_up_label.pack(side=tk.LEFT)
        
        def update_wheel_up_label(val):
            wheel_up_label.config(text=f"{float(val):.3f}")
        wheel_up_scale.configure(command=update_wheel_up_label)
        wheel_down_frame = ttk.Frame(dialog)
        wheel_down_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(wheel_down_frame, text="下滚轮阈值:").pack(side=tk.LEFT)
        wheel_down_var = tk.DoubleVar(value=current_thresholds['wheel_down_threshold'])
        wheel_down_scale = ttk.Scale(wheel_down_frame, from_=0.03, to=0.15, variable=wheel_down_var, orient=tk.HORIZONTAL)
        wheel_down_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        wheel_down_label = ttk.Label(wheel_down_frame, text=f"{wheel_down_var.get():.3f}")
        wheel_down_label.pack(side=tk.LEFT)

        def update_wheel_down_label(val):
            wheel_down_label.config(text=f"{float(val):.3f}")
        wheel_down_scale.configure(command=update_wheel_down_label)
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def apply_thresholds():
            self.hand_detector.update_gesture_thresholds(
                pinch=pinch_var.get(),
                fist=fist_var.get(),
                click_contact=click_var.get(),
                finger_proximity=proximity_var.get(),
                wheel_up=wheel_up_var.get(),
                wheel_down=wheel_down_var.get()
            )
            messagebox.showinfo("成功", "手势识别阈值已更新")
            dialog.destroy()
        def reset_thresholds():
            pinch_var.set(0.09)
            click_var.set(0.07)
            proximity_var.set(0.06)
            fist_var.set(0.15)
            wheel_up_var.set(0.08)
            wheel_down_var.set(0.08)
            update_pinch_label(0.09)
            update_click_label(0.07)
            update_proximity_label(0.06)
            update_fist_label(0.15)
            update_wheel_up_label(0.08)
            update_wheel_down_label(0.08)
        
        ttk.Button(button_frame, text="应用", command=apply_thresholds).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置", command=reset_thresholds).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _start_recognition(self):
        try:
            if self.hand_detector.initialize(self.config_manager):
                self.is_running = True
                self.is_paused = False
                self.controls_panel.update_control_states(running=True)
                self._update_status("运行中", "green")
                screen_width = self.config_manager.settings.screen_width.get()
                screen_height = self.config_manager.settings.screen_height.get()
                self.mouse_controller.update_screen_size(screen_width, screen_height)
                self.recognize_thread = threading.Thread(
                    target=self._recognition_loop, 
                    daemon=True
                )
                self.recognize_thread.start()
                self.logger.info("手势识别已启动")
            else:
                messagebox.showerror("错误", "无法初始化手部检测器")
        except Exception as e:
            self.logger.error(f"启动识别失败: {e}")
            messagebox.showerror("错误", f"启动识别失败: {e}")
    
    def _stop_recognition(self):
        self.is_running = False
        self.is_paused = False
        self.controls_panel.update_control_states(running=False)
        self._update_status("已停止", "red")
        self.hand_detector.cleanup()
        self.mouse_controller.release_all_buttons()
        self.logger.info("手势识别已停止")
    
    def _toggle_recognition(self):
        if self.is_running:
            self._stop_recognition()
        else:
            self._start_recognition()
    
    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self._update_status("已暂停", "orange")
            self.logger.info("识别已暂停")
        else:
            self._update_status("运行中", "green")
            self.logger.info("识别已恢复")
    
    def _toggle_mouse_control(self):
        self.mouse_control_enabled = not self.mouse_control_enabled
        if self.mouse_control_enabled:
            self.logger.info("鼠标控制已开启")
            self.controls_panel.update_mouse_status(True)
        else:
            self.mouse_controller.release_all_buttons()
            self.logger.info("鼠标控制已关闭")
            self.controls_panel.update_mouse_status(False)
    
    def _create_advanced_filter(self):
        return {
            'positions': deque(maxlen=6),
            'weights': [0.3, 0.25, 0.2, 0.15, 0.07, 0.03]
        }
    
    def _create_velocity_filter(self):
        return {
            'velocities': deque(maxlen=8),
            'accelerations': deque(maxlen=6)
        }
    
    def _assess_stability(self, x: float, y: float) -> bool:
        self.stability_window.append((x, y, time.perf_counter()))
        
        if len(self.stability_window) < self.min_stable_frames:
            return False
        recent_positions = list(self.stability_window)[-self.min_stable_frames:]
        displacements = []
        
        for i in range(1, len(recent_positions)):
            dx = recent_positions[i][0] - recent_positions[i-1][0]
            dy = recent_positions[i][1] - recent_positions[i-1][1]
            displacement = math.sqrt(dx*dx + dy*dy)
            displacements.append(displacement)
        avg_displacement = sum(displacements) / len(displacements)
        return avg_displacement < self.jitter_threshold
    def _predict_position(self, current_x: float, current_y: float, timestamp: float) -> Tuple[float, float]:
        self.position_history.append((current_x, current_y, timestamp))
        if len(self.position_history) > self.history_size:
            self.position_history.pop(0)
        
        if len(self.position_history) >= 3:
            if len(self.position_history) >= 6:
                positions = list(self.position_history)[-6:]
                velocities = []
                for i in range(1, len(positions)):
                    dx = positions[i][0] - positions[i-1][0]
                    dy = positions[i][1] - positions[i-1][1]
                    velocities.append((dx, dy))
                accelerations = []
                for i in range(1, len(velocities)):
                    ddx = velocities[i][0] - velocities[i-1][0]
                    ddy = velocities[i][1] - velocities[i-1][1]
                    accelerations.append((ddx, ddy))
                last_pos = positions[-1]
                last_vel = velocities[-1]
                last_acc = accelerations[-1] if accelerations else (0, 0)
                
                predicted_x = last_pos[0] + last_vel[0] + last_acc[0] * self.prediction_coefficient * 0.7
                predicted_y = last_pos[1] + last_vel[1] + last_acc[1] * self.prediction_coefficient * 0.7
            else:
                # three points
                p1, p2, p3 = list(self.position_history)[-3:]
                dx1 = p2[0] - p1[0]
                dy1 = p2[1] - p1[1]
                dx2 = p3[0] - p2[0]
                dy2 = p3[1] - p2[1]
                ddx = dx2 - dx1
                ddy = dy2 - dy1
                predicted_x = p3[0] + dx2 + ddx * self.prediction_coefficient * 0.8
                predicted_y = p3[1] + dy2 + ddy * self.prediction_coefficient * 0.8
        else:
            predicted_x, predicted_y = current_x, current_y
        
        return predicted_x, predicted_y
    
    def _apply_advanced_smoothing(self, x: float, y: float, timestamp: float) -> Tuple[float, float]:
        self.smoothing_filter['positions'].append((x, y, timestamp))
        if len(self.smoothing_filter['positions']) >= 3:
            weighted_x = 0
            weighted_y = 0
            positions = list(self.smoothing_filter['positions'])
            weights_to_use = self.smoothing_filter['weights'][:len(positions)]
            weight_sum = sum(weights_to_use)
            
            for i, (pos_x, pos_y, _) in enumerate(positions):
                if i < len(weights_to_use):
                    weight = weights_to_use[i] / weight_sum
                    weighted_x += pos_x * weight
                    weighted_y += pos_y * weight
            return weighted_x, weighted_y
        else:
            return x, y
    def _apply_conservative_smoothing(self, x: float, y: float) -> Tuple[float, float]:
        if self.last_result_cache:
            last_x, last_y = self.last_result_cache
            max_change = 0.02  # max change allowed 2%
            dx = max(-max_change, min(max_change, x - last_x))
            dy = max(-max_change, min(max_change, y - last_y))
            return last_x + dx, last_y + dy
        else:
            return x, y
    def _recognition_loop(self):
        target_fps = 60
        frame_interval = 1.0 / target_fps
        last_frame_time = time.time() 
        while self.is_running:
            current_time = time.time()
            if self.is_paused:
                time.sleep(frame_interval)
                continue
            try:
                elapsed = current_time - last_frame_time
                if elapsed < frame_interval:
                    time.sleep(frame_interval - elapsed)
                last_frame_time = time.time()
                frame, gesture, hand_landmarks = self.hand_detector.process_frame()
                if frame is not None:
                    self.preview_panel.update_preview(frame, hand_landmarks)
                    if self._should_process_gesture(gesture):
                        self._process_gesture_change(gesture, hand_landmarks)
            except Exception as e:
                self.logger.error(f"识别循环出错: {e}")
                if self.debug_mode:
                    print(f"[ERROR] 识别循环异常: {e}")
                time.sleep(0.01)
    
    def _should_process_gesture(self, current_gesture):
        current_time = time.time()
        if current_gesture != self.current_gesture:
            self.gesture_change_time = current_time
            self.current_gesture = current_gesture
            return True
        elif (current_time - self.gesture_change_time) >= self.gesture_stable_time:
            return True
        return False
    
    def _process_gesture_change(self, gesture, hand_landmarks):
        current_time = time.time()
        landmark_count = len(hand_landmarks.landmark) if hand_landmarks else 0
        self.preview_panel.update_gesture_display(gesture, landmark_count)
        if self.debug_mode:
            print(f"[GESTURE CHANGE] {self.previous_gesture} → {gesture}")
        if self.mouse_control_enabled:
            '''colldown time control'''
            cooldown_times = {
                "鼠标点击": 1.0,
                "鼠标右键": 1.0,
                "上滚轮": 1.0,
                "下滚轮": 1.0,
                "握拳": 0.5,
                "鼠标移动": 0.001
            }
            
            cooldown = cooldown_times.get(gesture, 0.1)
            last_execution = self.last_gesture_execution.get(gesture, 0)
            if current_time - last_execution >= cooldown:
                self._execute_gesture_action(gesture, hand_landmarks)
                self.last_gesture_execution[gesture] = current_time
            elif self.debug_mode:
                remaining = cooldown - (current_time - last_execution)
                print(f"[COOLDOWN] {gesture} 冷却中，剩余 {remaining:.2f}s")
        self.previous_gesture = gesture
    def _execute_gesture_action(self, gesture, hand_landmarks):
        try:
            if gesture == "鼠标移动":
                self._handle_mouse_movement(hand_landmarks)
            elif gesture in ["鼠标点击", "鼠标右键", "上滚轮", "下滚轮"]:
                self._handle_mouse_action(gesture)
            elif gesture == "握拳":
                self._handle_fist_gesture()
            else:
                hand_center = self.hand_detector.gesture_recognizer.get_hand_center()
                self.mouse_controller.handle_gesture(gesture, hand_center)
                
            if self.debug_mode:
                print(f"[EXECUTED] {gesture} 执行完成")
                
        except Exception as e:
            if self.debug_mode:
                print(f"[ERROR] 执行 {gesture} 失败: {e}")
    
    def _handle_mouse_movement(self, hand_landmarks):
        hand_center = self.hand_detector.gesture_recognizer.get_hand_center()
        if hand_center:
            point5_x, point5_y = hand_center
            screen_width, screen_height = 1920, 1080
            screen_x = int(point5_x * screen_width)
            screen_y = int(point5_y * screen_height)
            screen_x = max(0, min(screen_width, screen_x))
            screen_y = max(0, min(screen_height, screen_y))
            self.mouse_controller.mouse.position = (screen_x, screen_y)
            if self.debug_mode:
                print(f"[MOUSE MOVE] ({point5_x:.3f}, {point5_y:.3f}) → ({screen_x}, {screen_y})")
    
    def _handle_mouse_action(self, gesture):
        hand_center = self.hand_detector.gesture_recognizer.get_hand_center()
        try:
            self.mouse_controller.handle_gesture(gesture, hand_center)
        except Exception as e:
            if self.debug_mode:
                print(f"[MOUSE ACTION ERROR] {gesture}: {e}")
    
    def _handle_fist_gesture(self):
        self._toggle_mouse_control()
        if self.debug_mode:
            status = "暂停" if not self.mouse_control_enabled else "恢复"
    
    def _safe_update_preview(self, frame, gesture, hand_landmarks):
        try:
            self.preview_panel.update_preview(frame, hand_landmarks)
        except Exception as e:
            if self.debug_mode:
                print(f"[ERROR] 预览更新出错: {e}")
    
    def _update_detector(self):
        self.hand_detector.update_parameters(
            self.config_manager.settings.detection_confidence.get(),
            self.config_manager.settings.tracking_confidence.get()
        )
    
    def _update_gesture_display(self, gesture: str):
        self.current_gesture = gesture
    
    def _update_resolution_display(self):
        settings = self.config_manager.settings
        width = settings.screen_width.get()
        height = settings.screen_height.get()
        preset = settings.resolution_preset.get()
        
        if hasattr(self.controls_panel, 'resolution_display'):
            self.controls_panel.resolution_display.config(text=f"{width} x {height}")
    
    def _update_status(self, status: str, color: str):
        self.controls_panel.update_status(status, color)
        mouse_status = "开启" if self.mouse_control_enabled else "关闭"
        pause_status = "暂停" if self.is_paused else "运行"
        self.status_bar.config(
            text=f"状态: {status} | 手势: {self.current_gesture} | 鼠标: {mouse_status} | {pause_status}"
        )
    
    def _save_config(self):
        if self.config_manager.save_config():
            messagebox.showinfo("success", "配置已保存")
            self.logger.info("配置已保存")
        else:
            messagebox.showerror("error", "loading config failed")
    
    def _load_config_dialog(self):
        if self.config_manager.load_config():
            messagebox.showinfo("success", "successfully loaded config")
            self.logger.info("loading config successfully")
            self.controls_panel.refresh_display()
            self._update_resolution_display()
        else:
            messagebox.showerror("error", "loading config failed")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
使用说明:
1. 点击"启动识别"开始手势识别
2. 点击"开启鼠标控制"启用鼠标模拟
3. 使用手势控制鼠标:

   🖱️ 鼠标移动: 手掌移动控制光标位置
   💡 鼠标点击: 拇指+食指指尖触碰
   ⬇️ 下滚轮: 拇指尖触碰食指PIP关节（节点4和6）
   ⬆️ 上滚轮: 拇指尖触碰食指MCP关节（节点4和5）
   ✊ 握拳: 停止鼠标控制并释放按键

技术支持:
- 分辨率预设: 从下拉菜单中选择常用分辨率
- 摄像头扫描: 自动检测系统中的可用摄像头
- 摄像头选择: 可以选择使用哪个摄像头设备
- 骨架显示: 在预览窗口中可视化显示手部关键点
        """
        messagebox.showinfo("使用帮助", help_text)
    
    def _show_about(self):
        """显示关于信息"""
        about_text = """
FingerMouse Controller

基于 MediaPipe 和 OpenCV 的食指中指控制手势识别系统
支持智能点击和滚轮控制鼠标操作

作者: Zhao Yifan
开发语言: Python
GitHub: https://github.com/KrisitVvv/

主要功能:
- 智能手势识别(点击、滚轮、移动)
- 鼠标控制(移动、点击、滚轮)
        """
        messagebox.showinfo("关于", about_text)
    
    def _on_close(self):
        try:
            self.logger.info("程序正在关闭...")
            
            # 停止所有活动
            self.is_running = False
            self.is_paused = False
            
            # 清理资源
            self.hand_detector.cleanup()
            self.keyboard_listener.stop()
            self.mouse_controller.release_all_buttons()
            
            self.logger.info("资源已释放，程序退出")
            self.root.quit()
            
        except Exception as e:
            self.logger.error(f"关闭程序时出错: {e}")
            self.root.destroy()