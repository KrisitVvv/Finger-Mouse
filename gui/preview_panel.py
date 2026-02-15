#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import time
from typing import Callable, Optional, Any
class PreviewPanel:
    def __init__(self, parent: tk.Widget, gesture_callback: Callable[[str], None]):
        self.parent = parent
        self.gesture_callback = gesture_callback
        self.current_image: Optional[ImageTk.PhotoImage] = None
        self.hand_landmarks = None
        self.last_update_time = 0
        self.min_update_interval = 1/30 
        self.pending_update = None
        self._build_preview_area()
        self._build_status_area()
    def _build_preview_area(self):
        preview_frame = ttk.LabelFrame(self.parent, text="摄像头预览", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.preview_canvas = tk.Canvas(preview_frame, bg='black')
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        preview_ctrl_frame = ttk.Frame(preview_frame)
        preview_ctrl_frame.pack(fill=tk.X, pady=(5, 0))
        self.show_skeleton_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(preview_ctrl_frame, text="显示骨架", variable=self.show_skeleton_var).pack(side=tk.LEFT, padx=10)
    def _build_status_area(self):
        status_frame = ttk.LabelFrame(self.parent, text="状态信息", padding="5")
        status_frame.pack(fill=tk.X)
        gesture_frame = ttk.Frame(status_frame)
        gesture_frame.pack(fill=tk.X, pady=2)
        ttk.Label(gesture_frame, text="当前手势:", width=12).pack(side=tk.LEFT)
        self.gesture_label = ttk.Label(gesture_frame, text="无", foreground="blue")
        self.gesture_label.pack(side=tk.LEFT)
        skeleton_frame = ttk.Frame(status_frame)
        skeleton_frame.pack(fill=tk.X, pady=2)
        ttk.Label(skeleton_frame, text="关键点数:", width=12).pack(side=tk.LEFT)
        self.landmark_count_label = ttk.Label(skeleton_frame, text="0", foreground="gray")
        self.landmark_count_label.pack(side=tk.LEFT)
    
    def update_preview(self, frame, hand_landmarks=None):
        current_time = time.time()
        if current_time - self.last_update_time >= self.min_update_interval:
            self._perform_immediate_update(frame, hand_landmarks, current_time)
        else:
            self._schedule_delayed_update(frame, hand_landmarks, current_time)
    
    def _perform_immediate_update(self, frame, hand_landmarks, current_time):
        try:
            self.hand_landmarks = hand_landmarks
            self.last_update_time = current_time
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.show_skeleton_var.get() and hand_landmarks is not None:
                frame_rgb = self._draw_hand_skeleton(frame_rgb, hand_landmarks)
            img = Image.fromarray(frame_rgb)
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img_ratio = img.width / img.height
                canvas_ratio = canvas_width / canvas_height
                if img_ratio > canvas_ratio:
                    new_width = canvas_width
                    new_height = int(canvas_width / img_ratio)
                else:
                    new_height = canvas_height
                    new_width = int(canvas_height * img_ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                x_offset = (canvas_width - new_width) // 2
                y_offset = (canvas_height - new_height) // 2
                photo = ImageTk.PhotoImage(img)
                self.preview_canvas.delete("preview_image")
                self.preview_canvas.create_image(
                    x_offset, y_offset, 
                    anchor=tk.NW, 
                    image=photo,
                    tags="preview_image"
                )
                self.preview_canvas.image = photo
                if self.pending_update:
                    self.preview_canvas.after_cancel(self.pending_update)
                    self.pending_update = None
        except Exception as e:
            print(f"更新预览出错: {e}")
    
    def _schedule_delayed_update(self, frame, hand_landmarks, current_time):
        if self.pending_update:
            self.preview_canvas.after_cancel(self.pending_update)
        delay = int((self.min_update_interval - (current_time - self.last_update_time)) * 1000)
        self.pending_update = self.preview_canvas.after(delay, 
            lambda: self._perform_immediate_update(frame, hand_landmarks, time.time()))

    def _draw_hand_skeleton(self, frame_rgb, hand_landmarks):
        try:
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            h, w = frame.shape[:2]
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4), 
                (0, 5), (5, 6), (6, 7), (7, 8), 
                (0, 9), (9, 10), (10, 11), (11, 12),
                (0, 13), (13, 14), (14, 15), (15, 16), 
                (0, 17), (17, 18), (18, 19), (19, 20), 
                (5, 9), (9, 13), (13, 17), 
                (4, 8), (8, 12), (12, 16), (16, 20)
            ]
            
            for connection in connections:
                start_idx, end_idx = connection
                if start_idx < len(hand_landmarks.landmark) and end_idx < len(hand_landmarks.landmark):
                    start_point = hand_landmarks.landmark[start_idx]
                    end_point = hand_landmarks.landmark[end_idx]
                    start_x, start_y = int(start_point.x * w), int(start_point.y * h)
                    end_x, end_y = int(end_point.x * w), int(end_point.y * h)
                    cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2, cv2.LINE_AA)
            for idx, landmark in enumerate(hand_landmarks.landmark):
                if idx < len(hand_landmarks.landmark):
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    if idx in [4, 8, 12, 16, 20]: 
                        color = (0, 0, 255) 
                        radius = 4
                    elif idx == 0: 
                        color = (255, 0, 0)
                        radius = 6
                    else: 
                        color = (0, 255, 255) 
                        radius = 3
                    cv2.circle(frame, (x, y), radius, color, -1, cv2.LINE_AA)
                    cv2.putText(frame, str(idx), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"绘制骨架出错: {e}")
            return frame_rgb
    
    def update_gesture_display(self, gesture: str, landmark_count: int = 0):
        self.gesture_label.config(text=gesture)
        self.landmark_count_label.config(text=str(landmark_count))
        color_map = {
            "无": "gray",
            "捏合": "blue",
            "握拳": "red",
            "手掌张开": "green",
        }
        color = color_map.get(gesture, "black")
        self.gesture_label.config(foreground=color)
        if self.gesture_callback:
            self.gesture_callback(gesture)