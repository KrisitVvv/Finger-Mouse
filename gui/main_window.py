#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主窗口类
负责整个GUI界面的构建和管理，支持食指中指控制功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional

from config import ConfigManager
from utils.logger import setup_logger
from recognition.hand_detector import HandDetector
from control.mouse_controller import MouseController
from control.keyboard_listener import KeyboardListener
from .controls_panel import ControlsPanel
from .preview_panel import PreviewPanel


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Windows 手势识别鼠标控制器")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # 初始化核心组件
        self.logger = setup_logger()
        # 添加调试模式开关（默认关闭以提高性能）
        self.debug_mode = False
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        # 使用根窗口初始化配置管理器
        self.config_manager.initialize_with_root(root)
        self.hand_detector = HandDetector()
        self.mouse_controller = MouseController()
        self.keyboard_listener = KeyboardListener(self._toggle_recognition)
        
        # 状态变量
        self.is_running = False
        self.mouse_control_enabled = False
        self.is_paused = False
        self.recognize_thread: Optional[threading.Thread] = None
        self.current_gesture = "无"
        
        # 加载配置
        self.config_manager.load_config()
        
        # 构建GUI界面
        self._build_gui()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 启动键盘监听
        self.keyboard_listener.start()
        
        # 初始化分辨率显示
        self._update_resolution_display()
        
        self.logger.info("主窗口初始化完成")
    
    def _build_gui(self):
        """构建GUI界面"""
        # 创建菜单栏
        self._create_menu()
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        self.controls_panel = ControlsPanel(
            main_frame, 
            self.config_manager,
            self._start_recognition,
            self._stop_recognition,
            self._toggle_pause,
            self._toggle_mouse_control,
            self._update_detector
        )
        
        # 右侧预览和状态区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 预览面板
        self.preview_panel = PreviewPanel(right_frame, self._update_gesture_display)
        
        # 状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存配置", command=self._save_config)
        file_menu.add_command(label="加载配置", command=self._load_config_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_close)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="手势识别阈值", command=self._show_gesture_thresholds_dialog)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _show_gesture_thresholds_dialog(self):
        """显示手势识别阈值设置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("手势识别阈值设置")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 获取当前阈值
        current_thresholds = self.hand_detector.gesture_recognizer.get_thresholds()
        
        # 创建设置界面
        ttk.Label(dialog, text="调整手势识别的敏感度阈值:", font=("Arial", 12)).pack(pady=10)
        
        # 精确触碰阈值
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
        
        # 点击接触阈值
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
        
        # 手指靠近阈值
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
        
        # 握拳阈值
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
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def apply_thresholds():
            """应用阈值设置"""
            self.hand_detector.update_gesture_thresholds(
                pinch=pinch_var.get(),
                fist=fist_var.get(),
                click_contact=click_var.get(),
                finger_proximity=proximity_var.get()
            )
            messagebox.showinfo("成功", "手势识别阈值已更新")
            dialog.destroy()
        
        def reset_thresholds():
            """重置为默认值"""
            pinch_var.set(0.06)
            click_var.set(0.05)
            proximity_var.set(0.04)
            fist_var.set(0.12)
            update_pinch_label(0.06)
            update_click_label(0.05)
            update_proximity_label(0.04)
            update_fist_label(0.12)
        
        ttk.Button(button_frame, text="应用", command=apply_thresholds).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置", command=reset_thresholds).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _start_recognition(self):
        """启动手势识别"""
        try:
            if self.hand_detector.initialize(self.config_manager):
                self.is_running = True
                self.is_paused = False
                self.controls_panel.update_control_states(running=True)
                self._update_status("运行中", "green")
                
                # 更新鼠标控制器的屏幕尺寸
                screen_width = self.config_manager.settings.screen_width.get()
                screen_height = self.config_manager.settings.screen_height.get()
                self.mouse_controller.update_screen_size(screen_width, screen_height)
                
                # 启动识别线程
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
        """停止手势识别"""
        self.is_running = False
        self.is_paused = False
        self.controls_panel.update_control_states(running=False)
        self._update_status("已停止", "red")
        self.hand_detector.cleanup()
        self.mouse_controller.release_all_buttons()
        self.logger.info("手势识别已停止")
    
    def _toggle_recognition(self):
        """切换识别状态"""
        if self.is_running:
            self._stop_recognition()
        else:
            self._start_recognition()
    
    def _toggle_pause(self):
        """切换暂停状态"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self._update_status("已暂停", "orange")
            self.logger.info("识别已暂停")
        else:
            self._update_status("运行中", "green")
            self.logger.info("识别已恢复")
    
    def _toggle_mouse_control(self):
        """切换鼠标控制状态"""
        self.mouse_control_enabled = not self.mouse_control_enabled
        if self.mouse_control_enabled:
            self.logger.info("鼠标控制已开启")
            # 更新界面显示
            self.controls_panel.update_mouse_status(True)
        else:
            self.mouse_controller.release_all_buttons()
            self.logger.info("鼠标控制已关闭")
            # 更新界面显示
            self.controls_panel.update_mouse_status(False)
    
    def _recognition_loop(self):
        """手势识别主循环 - 优化版（减少闪烁，提高流畅度）"""
        # 优化帧率控制参数
        target_fps = 60  # 保持60FPS
        frame_interval = 1.0 / target_fps  # 约16.67ms
        
        # 帧缓冲机制
        frame_queue = []
        max_queue_size = 3  # 最大队列大小
        
        while self.is_running:
            loop_start_time = time.time()
            
            if self.is_paused:
                time.sleep(frame_interval)
                continue
                
            try:
                # 获取摄像头帧并处理
                frame, gesture, hand_landmarks = self.hand_detector.process_frame()
                if frame is not None:
                    # 帧缓冲管理
                    frame_queue.append((frame, gesture, hand_landmarks))
                    if len(frame_queue) > max_queue_size:
                        frame_queue.pop(0)  # 移除最老的帧
                    
                    # 只处理最新的帧进行显示更新
                    latest_frame, latest_gesture, latest_landmarks = frame_queue[-1]
                    
                    # 使用after_idle在GUI空闲时更新显示，减少闪烁
                    self.root.after_idle(
                        lambda f=latest_frame.copy(), g=latest_gesture, l=latest_landmarks: 
                        self._safe_update_preview(f, g, l)
                    )
                    
                    # 处理手势逻辑（在后台线程中）
                    if latest_gesture != self.current_gesture:
                        self.current_gesture = latest_gesture
                        landmark_count = len(latest_landmarks.landmark) if latest_landmarks else 0
                        
                        # 异步更新手势显示
                        self.root.after_idle(
                            lambda g=latest_gesture, c=landmark_count: 
                            self.preview_panel.update_gesture_display(g, c)
                        )
                        
                        # 鼠标控制处理
                        if self.mouse_control_enabled:
                            hand_center = self.hand_detector.gesture_recognizer.get_hand_center()
                            
                            # 鼠标移动手势的优化处理
                            if latest_gesture == "鼠标移动" and hand_center:
                                point5_x, point5_y = hand_center
                                screen_width, screen_height = 1920, 1080
                                screen_x = int(point5_x * screen_width)
                                screen_y = int(point5_y * screen_height)
                                screen_x = max(0, min(screen_width, screen_x))
                                screen_y = max(0, min(screen_height, screen_y))
                                
                                # 直接移动鼠标
                                self.mouse_controller.mouse.position = (screen_x, screen_y)
                            else:
                                # 其他手势使用标准处理
                                try:
                                    self.mouse_controller.handle_gesture(latest_gesture, hand_center)
                                except Exception as e:
                                    if self.debug_mode:
                                        print(f"[ERROR] 手势执行出错: {e}")
                
                # 精确的帧率控制
                loop_end_time = time.time()
                processing_time = loop_end_time - loop_start_time
                sleep_time = max(0, frame_interval - processing_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"识别循环出错: {e}")
                if self.debug_mode:
                    print(f"[ERROR] 识别循环异常: {e}")
                    import traceback
                    traceback.print_exc()
                time.sleep(0.01)  # 出错时短暂延迟
    
    def _safe_update_preview(self, frame, gesture, hand_landmarks):
        """安全的预览更新方法"""
        try:
            self.preview_panel.update_preview(frame, hand_landmarks)
        except Exception as e:
            if self.debug_mode:
                print(f"[ERROR] 预览更新出错: {e}")
    
    def _update_detector(self):
        """更新手部检测器参数"""
        self.hand_detector.update_parameters(
            self.config_manager.settings.detection_confidence.get(),
            self.config_manager.settings.tracking_confidence.get()
        )
    
    def _update_gesture_display(self, gesture: str):
        """更新手势显示"""
        self.current_gesture = gesture
        # 这里不再直接调用preview_panel的update_gesture_display，因为已经在识别循环中处理了
    
    def _update_resolution_display(self):
        """更新分辨率显示"""
        settings = self.config_manager.settings
        width = settings.screen_width.get()
        height = settings.screen_height.get()
        preset = settings.resolution_preset.get()
        
        # 更新控制面板中的分辨率显示
        if hasattr(self.controls_panel, 'resolution_display'):
            self.controls_panel.resolution_display.config(text=f"{width} x {height}")
    
    def _update_status(self, status: str, color: str):
        """更新状态显示"""
        self.controls_panel.update_status(status, color)
        mouse_status = "开启" if self.mouse_control_enabled else "关闭"
        pause_status = "暂停" if self.is_paused else "运行"
        self.status_bar.config(
            text=f"状态: {status} | 手势: {self.current_gesture} | 鼠标: {mouse_status} | {pause_status}"
        )
    
    def _save_config(self):
        """保存配置"""
        if self.config_manager.save_config():
            messagebox.showinfo("成功", "配置已保存")
            self.logger.info("配置已保存")
        else:
            messagebox.showerror("错误", "保存配置失败")
    
    def _load_config_dialog(self):
        """加载配置对话框"""
        # 这里可以添加文件选择对话框
        if self.config_manager.load_config():
            messagebox.showinfo("成功", "配置已加载")
            self.logger.info("配置已加载")
            # 更新界面显示
            self.controls_panel.refresh_display()
            self._update_resolution_display()
        else:
            messagebox.showerror("错误", "加载配置失败")
    
    def _show_help(self):
        """显示帮助信息（包含新的手腕控制功能）"""
        help_text = """
使用说明:
1. 点击"启动识别"开始手势识别
2. 点击"开启鼠标控制"启用鼠标模拟
3. 使用手腕控制鼠标:

   🖱️ 鼠标移动: 手腕移动控制光标位置
   💡 鼠标点击: 拇指+食指指尖触碰
   ⬇️ 下滚轮: 拇指尖触碰食指DIP关节
   ⬆️ 上滚轮: 拇指尖触碰食指PIP关节
   ✊ 握拳: 停止鼠标控制并释放按键（最高优先级）
   🏠 回到桌面: 张开手掌→握拳(过渡手势)

重要特性:
- 手腕移动即可控制鼠标，无需张开手掌
- 握拳手势具有最高优先级，立即停止所有鼠标控制
- 0.5秒后自动恢复控制（防止误操作）
- 其他手势功能保持不变

4. 可通过参数面板调整识别灵敏度
5. 支持热键 Ctrl+Alt+G 切换识别状态

新增功能:
- 🔄 手腕坐标控制: 更自然的手势控制体验
- ⚡ 握拳急停: 紧急情况下快速停止鼠标控制
- 🎯 优先级管理: 握拳 > 点击 > 滚轮 > 移动
- 🛡️ 智能恢复: 自动恢复控制避免长时间禁用

高级功能:
- 双击手势: 快速两次捏合执行双击
- 组合手势: 支持复杂的手势序列识别
- 快捷键映射: 可将手势映射到任意键盘快捷键
- 动态配置: 运行时可修改手势映射关系

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
手势识别鼠标控制器 v4.1

基于 MediaPipe 和 OpenCV 的食指中指控制手势识别系统
支持智能点击和滚轮控制鼠标操作

作者: AI Assistant
开发语言: Python

主要功能:
- 智能手势识别(点击、滚轮、移动)
- 鼠标控制(移动、点击、滚轮)
- 实时预览和参数调节
- 多摄像头支持和分辨率选择
- 可调节的手指控制阈值
- 手部骨架可视化显示
- 新增食指中指靠近移动机制
        """
        messagebox.showinfo("关于", about_text)
    
    def _on_close(self):
        """窗口关闭处理"""
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