#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
预览面板类
负责摄像头预览和手势显示，包含骨架可视化功能
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
from typing import Callable, Optional, Any


class PreviewPanel:
    """预览面板类"""
    
    def __init__(self, parent: tk.Widget, gesture_callback: Callable[[str], None]):
        self.parent = parent
        self.gesture_callback = gesture_callback
        self.current_image: Optional[ImageTk.PhotoImage] = None
        self.hand_landmarks = None  # 存储手部关键点数据
        
        # 构建预览区域
        self._build_preview_area()
        self._build_status_area()
    
    def _build_preview_area(self):
        """构建预览区域"""
        preview_frame = ttk.LabelFrame(self.parent, text="摄像头预览", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建画布用于显示图像
        self.preview_canvas = tk.Canvas(preview_frame, bg='black')
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 添加预览控制
        preview_ctrl_frame = ttk.Frame(preview_frame)
        preview_ctrl_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(preview_ctrl_frame, text="截图保存", command=self._save_screenshot).pack(side=tk.LEFT, padx=2)
        ttk.Button(preview_ctrl_frame, text="刷新摄像头", command=self._refresh_camera).pack(side=tk.LEFT, padx=2)
        
        # 骨架显示开关
        self.show_skeleton_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(preview_ctrl_frame, text="显示骨架", variable=self.show_skeleton_var).pack(side=tk.LEFT, padx=10)
    
    def _build_status_area(self):
        """构建状态显示区域"""
        status_frame = ttk.LabelFrame(self.parent, text="状态信息", padding="5")
        status_frame.pack(fill=tk.X)
        
        # 手势状态
        gesture_frame = ttk.Frame(status_frame)
        gesture_frame.pack(fill=tk.X, pady=2)
        ttk.Label(gesture_frame, text="当前手势:", width=12).pack(side=tk.LEFT)
        self.gesture_label = ttk.Label(gesture_frame, text="无", foreground="blue")
        self.gesture_label.pack(side=tk.LEFT)
        
        # 骨架信息
        skeleton_frame = ttk.Frame(status_frame)
        skeleton_frame.pack(fill=tk.X, pady=2)
        ttk.Label(skeleton_frame, text="关键点数:", width=12).pack(side=tk.LEFT)
        self.landmark_count_label = ttk.Label(skeleton_frame, text="0", foreground="gray")
        self.landmark_count_label.pack(side=tk.LEFT)
    
    def update_preview(self, frame, hand_landmarks=None):
        """更新预览画面 - 优化版（减少闪烁）"""
        try:
            # 保存手部关键点数据
            self.hand_landmarks = hand_landmarks
            
            # 转换为PhotoImage格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 如果需要显示骨架，在这里绘制
            if self.show_skeleton_var.get() and hand_landmarks is not None:
                frame_rgb = self._draw_hand_skeleton(frame_rgb, hand_landmarks)
            
            img = Image.fromarray(frame_rgb)
            
            # 获取画布尺寸
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # 确保画布已初始化
                # 保持宽高比缩放
                img_ratio = img.width / img.height
                canvas_ratio = canvas_width / canvas_height
                
                if img_ratio > canvas_ratio:
                    new_width = canvas_width
                    new_height = int(canvas_width / img_ratio)
                else:
                    new_height = canvas_height
                    new_width = int(canvas_height * img_ratio)
                
                # 使用高质量重采样
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 居中显示
                x_offset = (canvas_width - new_width) // 2
                y_offset = (canvas_height - new_height) // 2
                
                # 双缓冲机制：先创建新图像，再替换旧图像
                photo = ImageTk.PhotoImage(img)
                
                # 批量更新画布，减少闪烁
                self.preview_canvas.delete("preview_image")
                self.preview_canvas.create_image(
                    x_offset, y_offset, 
                    anchor=tk.NW, 
                    image=photo,
                    tags="preview_image"  # 添加标签以便精确删除
                )
                self.preview_canvas.image = photo  # 保持引用
                
        except Exception as e:
            print(f"更新预览出错: {e}")
    
    def _draw_hand_skeleton(self, frame_rgb, hand_landmarks):
        """绘制手部骨架 - 优化版"""
        try:
            # 转换为OpenCV格式进行绘制
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            h, w = frame.shape[:2]
            
            # 定义手部连接关系
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),  # 拇指
                (0, 5), (5, 6), (6, 7), (7, 8),  # 食指
                (0, 9), (9, 10), (10, 11), (11, 12),  # 中指
                (0, 13), (13, 14), (14, 15), (15, 16),  # 无名指
                (0, 17), (17, 18), (18, 19), (19, 20),  # 小指
                # 手掌连接
                (5, 9), (9, 13), (13, 17),  # 手指基部连接
                (4, 8), (8, 12), (12, 16), (16, 20)  # 手指尖连接
            ]
            
            # 绘制连接线
            for connection in connections:
                start_idx, end_idx = connection
                if start_idx < len(hand_landmarks.landmark) and end_idx < len(hand_landmarks.landmark):
                    start_point = hand_landmarks.landmark[start_idx]
                    end_point = hand_landmarks.landmark[end_idx]
                    
                    # 转换为像素坐标
                    start_x, start_y = int(start_point.x * w), int(start_point.y * h)
                    end_x, end_y = int(end_point.x * w), int(end_point.y * h)
                    
                    # 绘制连线（使用抗锯齿）
                    cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2, cv2.LINE_AA)
            
            # 绘制关键点
            for idx, landmark in enumerate(hand_landmarks.landmark):
                if idx < len(hand_landmarks.landmark):
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    # 不同关键点用不同颜色标记
                    if idx in [4, 8, 12, 16, 20]:  # 手指尖
                        color = (0, 0, 255)  # 红色
                        radius = 4
                    elif idx == 0:  # 手腕
                        color = (255, 0, 0)  # 蓝色
                        radius = 6
                    else:  # 其他关节
                        color = (0, 255, 255)  # 黄色
                        radius = 3
                    
                    # 绘制圆形关键点（使用抗锯齿）
                    cv2.circle(frame, (x, y), radius, color, -1, cv2.LINE_AA)
                    # 添加关键点编号
                    cv2.putText(frame, str(idx), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)
            
            # 转换回RGB格式
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
        except Exception as e:
            print(f"绘制骨架出错: {e}")
            return frame_rgb
    
    def update_gesture_display(self, gesture: str, landmark_count: int = 0):
        """更新手势显示"""
        self.gesture_label.config(text=gesture)
        
        # 更新关键点数量显示
        self.landmark_count_label.config(text=str(landmark_count))
        
        # 不同手势不同颜色
        color_map = {
            "无": "gray",
            "捏合": "blue",
            "握拳": "red",
            "手掌张开": "green",
            "V字手势": "purple",
            "OK手势": "orange"
        }
        color = color_map.get(gesture, "black")
        self.gesture_label.config(foreground=color)
        
        # 调用回调函数
        if self.gesture_callback:
            self.gesture_callback(gesture)
    
    def _save_screenshot(self):
        """保存截图"""
        # 这里需要访问摄像头帧数据
        print("截图功能待实现")
    
    def _refresh_camera(self):
        """刷新摄像头"""
        # 这里需要重新初始化摄像头
        print("刷新摄像头功能待实现")