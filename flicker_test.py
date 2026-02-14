#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
摄像头闪烁测试脚本
验证画面闪烁问题的修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np


class FlickerTestWindow:
    """闪烁测试窗口"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("摄像头闪烁测试")
        self.root.geometry("800x600")
        
        # 测试参数
        self.test_duration = 10  # 测试持续时间（秒）
        self.frame_count = 0
        self.start_time = None
        self.is_testing = False
        
        # 构建界面
        self._build_ui()
        
        # 初始化摄像头
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("无法打开摄像头")
            return
            
        # 设置摄像头参数
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("摄像头初始化成功")
    
    def _build_ui(self):
        """构建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="摄像头闪烁测试", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 测试控制区域
        control_frame = ttk.LabelFrame(main_frame, text="测试控制", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="开始测试", command=self._start_test)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止测试", command=self._stop_test, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # 参数设置
        param_frame = ttk.Frame(control_frame)
        param_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        ttk.Label(param_frame, text="测试时长:").pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value="10")
        duration_entry = ttk.Entry(param_frame, textvariable=self.duration_var, width=5)
        duration_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(param_frame, text="秒").pack(side=tk.LEFT, padx=(2, 0))
        
        # 显示区域
        display_frame = ttk.LabelFrame(main_frame, text="摄像头预览", padding="5")
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.canvas = tk.Canvas(display_frame, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 状态信息
        status_frame = ttk.LabelFrame(main_frame, text="测试状态", padding="10")
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="准备就绪")
        self.status_label.pack()
        
        self.fps_label = ttk.Label(status_frame, text="FPS: --")
        self.fps_label.pack()
        
        self.frame_label = ttk.Label(status_frame, text="帧数: 0")
        self.frame_label.pack()
        
        # 统计信息
        stats_frame = ttk.LabelFrame(main_frame, text="闪烁检测结果", padding="10")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.result_text = tk.Text(stats_frame, height=8, width=60)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar.set)
    
    def _start_test(self):
        """开始测试"""
        try:
            self.test_duration = int(self.duration_var.get())
        except ValueError:
            self.test_duration = 10
            
        self.is_testing = True
        self.frame_count = 0
        self.start_time = time.time()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"测试进行中... ({self.test_duration}秒)")
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"开始测试，持续时间: {self.test_duration}秒\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n")
        
        # 开始测试循环
        self._test_loop()
    
    def _stop_test(self):
        """停止测试"""
        self.is_testing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="测试已停止")
    
    def _test_loop(self):
        """测试主循环"""
        if not self.is_testing:
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        if elapsed_time >= self.test_duration:
            self._finish_test()
            return
        
        try:
            # 获取摄像头帧
            ret, frame = self.cap.read()
            if ret:
                self.frame_count += 1
                
                # 更新显示
                self._update_display(frame)
                
                # 计算实时FPS
                if self.frame_count > 1:  # 跳过第一帧
                    current_fps = self.frame_count / elapsed_time
                    self.fps_label.config(text=f"FPS: {current_fps:.1f}")
                    self.frame_label.config(text=f"帧数: {self.frame_count}")
                
                # 检测可能的闪烁情况
                self._detect_flicker(frame, elapsed_time)
            
            # 继续测试循环
            self.root.after(16, self._test_loop)  # 约60FPS
            
        except Exception as e:
            print(f"测试过程中出错: {e}")
            self._stop_test()
    
    def _update_display(self, frame):
        """更新显示 - 优化版（减少闪烁）"""
        try:
            # 转换为RGB格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # 获取画布尺寸
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
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
                self.canvas.delete("preview_image")
                self.canvas.create_image(
                    x_offset, y_offset,
                    anchor=tk.NW,
                    image=photo,
                    tags="preview_image"
                )
                self.canvas.image = photo  # 保持引用
                
        except Exception as e:
            print(f"更新显示出错: {e}")
    
    def _detect_flicker(self, frame, elapsed_time):
        """检测闪烁情况"""
        try:
            # 计算图像亮度均值
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # 每秒记录一次亮度信息
            if int(elapsed_time) > int(elapsed_time - 1/30):  # 每帧检查
                timestamp = f"{elapsed_time:.2f}s"
                info = f"[{timestamp}] 亮度: {brightness:.1f}"
                
                # 检测亮度突变（可能的闪烁）
                if hasattr(self, '_last_brightness'):
                    brightness_diff = abs(brightness - self._last_brightness)
                    if brightness_diff > 30:  # 亮度变化超过阈值
                        info += f" ⚠️ 亮度突变 (+{brightness_diff:.1f})"
                        self.result_text.insert(tk.END, info + "\n")
                        self.result_text.see(tk.END)
                
                self._last_brightness = brightness
                
        except Exception as e:
            print(f"闪烁检测出错: {e}")
    
    def _finish_test(self):
        """完成测试"""
        self.is_testing = False
        total_time = time.time() - self.start_time
        average_fps = self.frame_count / total_time if total_time > 0 else 0
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="测试完成")
        
        # 显示最终统计
        self.result_text.insert(tk.END, "\n" + "=" * 50 + "\n")
        self.result_text.insert(tk.END, "测试完成统计:\n")
        self.result_text.insert(tk.END, f"总帧数: {self.frame_count}\n")
        self.result_text.insert(tk.END, f"测试时长: {total_time:.2f}秒\n")
        self.result_text.insert(tk.END, f"平均FPS: {average_fps:.1f}\n")
        
        if average_fps >= 25:
            self.result_text.insert(tk.END, "✅ 帧率表现良好\n")
        elif average_fps >= 15:
            self.result_text.insert(tk.END, "⚠️ 帧率一般，可能有轻微卡顿\n")
        else:
            self.result_text.insert(tk.END, "❌ 帧率较低，可能存在明显卡顿\n")
        
        self.result_text.insert(tk.END, "\n闪烁检测建议:\n")
        self.result_text.insert(tk.END, "• 如果看到⚠️标记，表示可能有亮度突变\n")
        self.result_text.insert(tk.END, "• 正常情况下亮度应该相对稳定\n")
        self.result_text.insert(tk.END, "• 频繁的亮度突变可能表明画面闪烁\n")
        
        self.result_text.see(tk.END)
    
    def run(self):
        """运行测试窗口"""
        try:
            self.root.mainloop()
        finally:
            if self.cap:
                self.cap.release()


def main():
    """主函数"""
    print("摄像头闪烁测试工具")
    print("=" * 30)
    print("此工具可以帮助检测和分析摄像头画面闪烁问题")
    print("请确保摄像头已正确连接")
    print()
    
    try:
        app = FlickerTestWindow()
        app.run()
    except Exception as e:
        print(f"程序运行出错: {e}")


if __name__ == "__main__":
    main()