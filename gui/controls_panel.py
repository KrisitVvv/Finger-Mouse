import cv2
import platform
from typing import List, Tuple
import tkinter as tk
from tkinter import ttk
from typing import Callable, Any
from config import ConfigManager
from utils.camera_scanner import CameraScanner

class CameraScanner:    
    def __init__(self):
        self.system = platform.system().lower()
    
    def get_resolution_presets(self) -> List[str]:
        return [
            "自定义",
            "480p (640x480)",
            "720p (1280x720)", 
            "1080p (1920x1080)",
            "1440p (2560x1440)",
            "4K (3840x2160)"
        ]
    
    def get_resolution_by_name(self, name: str) -> Tuple[int, int]:
        resolutions = {
            "自定义": (800, 600),
            "480p (640x480)": (640, 480),
            "720p (1280x720)": (1280, 720),
            "1080p (1920x1080)": (1920, 1080),
            "1440p (2560x1440)": (2560, 1440),
            "4K (3840x2160)": (3840, 2160)
        }
        return resolutions.get(name, (800, 600))
    
    def scan_cameras(self) -> List[Tuple[int, str]]:
        available_cameras = []
        if self.system == "windows":
            for i in range(10):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        available_cameras.append((i, f"摄像头 {i}"))
                    cap.release()
        elif self.system == "darwin":
            for i in range(5):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        available_cameras.append((i, f"内置摄像头" if i == 0 else f"外部摄像头 {i}"))
                    cap.release()
        else:
            for i in range(10):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        available_cameras.append((i, f"/dev/video{i}"))
                    cap.release()
        
        return available_cameras if available_cameras else []

class ControlsPanel:    
    def __init__(self, parent: tk.Widget, config_manager: ConfigManager,
                 start_callback: Callable, stop_callback: Callable,
                 pause_callback: Callable, mouse_callback: Callable,
                 update_callback: Callable):
        self.parent = parent
        self.config_manager = config_manager
        self.callbacks = {
            'start': start_callback,
            'stop': stop_callback,
            'pause': pause_callback,
            'mouse': mouse_callback,
            'update': update_callback
        }
        self.camera_scanner = CameraScanner()
        self.available_cameras = []
        self.control_widgets = {}
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self._build_parameter_controls(control_frame)
        self._build_control_buttons(control_frame)
        self._build_status_display(control_frame)
    
    def _build_parameter_controls(self, parent: tk.Widget):
        param_frame = ttk.LabelFrame(parent, text="参数设置", padding="5")
        param_frame.pack(fill=tk.X, pady=(0, 10))
        settings = self.config_manager.settings
        ttk.Label(param_frame, text="检测置信度:").grid(row=0, column=0, sticky=tk.W, pady=2)
        detection_slider = ttk.Scale(
            param_frame, from_=0.5, to=0.9, variable=settings.detection_confidence,
            command=lambda v: self.callbacks['update']()
        )
        detection_slider.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=settings.detection_confidence).grid(row=0, column=2, padx=5)
        ttk.Label(param_frame, text="跟踪置信度:").grid(row=1, column=0, sticky=tk.W, pady=2)
        tracking_slider = ttk.Scale(
            param_frame, from_=0.5, to=0.9, variable=settings.tracking_confidence,
            command=lambda v: self.callbacks['update']()
        )
        tracking_slider.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=settings.tracking_confidence).grid(row=1, column=2, padx=5)
        ttk.Label(param_frame, text="捏合阈值:").grid(row=2, column=0, sticky=tk.W, pady=2)
        pinching_slider = ttk.Scale(param_frame, from_=0.01, to=0.1, variable=settings.pinching_threshold)
        pinching_slider.grid(row=2, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=settings.pinching_threshold).grid(row=2, column=2, padx=5)
        ttk.Label(param_frame, text="握拳阈值:").grid(row=3, column=0, sticky=tk.W, pady=2)
        fist_slider = ttk.Scale(param_frame, from_=0.05, to=0.15, variable=settings.fist_threshold)
        fist_slider.grid(row=3, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=settings.fist_threshold).grid(row=3, column=2, padx=5)
        ttk.Label(param_frame, text="平滑因子:").grid(row=4, column=0, sticky=tk.W, pady=2)
        smoothing_slider = ttk.Scale(param_frame, from_=0.1, to=0.8, variable=settings.smoothing_factor)
        smoothing_slider.grid(row=4, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=settings.smoothing_factor).grid(row=4, column=2, padx=5)
        ttk.Label(param_frame, text="滚动灵敏度:").grid(row=5, column=0, sticky=tk.W, pady=2)
        scroll_slider = ttk.Scale(param_frame, from_=0.5, to=2.0, variable=settings.scroll_sensitivity)
        scroll_slider.grid(row=5, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=settings.scroll_sensitivity).grid(row=5, column=2, padx=5)
        screen_frame = ttk.LabelFrame(parent, text="屏幕设置", padding="5")
        screen_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(screen_frame, text="目标分辨率:").grid(row=0, column=0, sticky=tk.W, pady=2)
        resolution_presets = self.camera_scanner.get_resolution_presets()
        self.resolution_combo = ttk.Combobox(
            screen_frame, 
            textvariable=settings.resolution_preset,
            values=resolution_presets,
            state="readonly",
            width=20
        )
        self.resolution_combo.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        self.resolution_combo.bind('<<ComboboxSelected>>', self._on_resolution_change)
        resolution_frame = ttk.Frame(screen_frame)
        resolution_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=2)
        ttk.Label(resolution_frame, text="当前设置:").pack(side=tk.LEFT)
        self.resolution_display = ttk.Label(
            resolution_frame, 
            text=f"{settings.screen_width.get()} x {settings.screen_height.get()}"
        )
        self.resolution_display.pack(side=tk.LEFT, padx=(5, 0))
        camera_frame = ttk.LabelFrame(parent, text="摄像头设置", padding="5")
        camera_frame.pack(fill=tk.X, pady=(0, 10))
        scan_frame = ttk.Frame(camera_frame)
        scan_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=2)
        self.scan_btn = ttk.Button(scan_frame, text="扫描摄像头", command=self._scan_cameras)
        self.scan_btn.pack(side=tk.LEFT)
        self.camera_status = ttk.Label(scan_frame, text="未扫描")
        self.camera_status.pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(camera_frame, text="选择摄像头:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.camera_combo = ttk.Combobox(
            camera_frame,
            textvariable=settings.camera_index,
            state="readonly",
            width=20
        )
        self.camera_combo.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)
        self.camera_combo.bind('<<ComboboxSelected>>', self._on_camera_change)
        ttk.Label(camera_frame, text="摄像头分辨率:").grid(row=2, column=0, sticky=tk.W, pady=2)
        
        cam_resolutions = ["640x480", "800x600", "1280x720", "1920x1080"]
        self.cam_resolution_combo = ttk.Combobox(
            camera_frame,
            values=cam_resolutions,
            state="readonly",
            width=20
        )
        self.cam_resolution_combo.set("1920x1080")
        self.cam_resolution_combo.grid(row=2, column=1, padx=5, pady=2, sticky=tk.EW)
        self.cam_resolution_combo.bind('<<ComboboxSelected>>', self._on_cam_resolution_change)
        ttk.Label(camera_frame, text="帧率:").grid(row=3, column=0, sticky=tk.W, pady=2)
        fps_entry = ttk.Entry(camera_frame, textvariable=settings.camera_fps, width=10)
        fps_entry.grid(row=3, column=1, padx=5, pady=2)
    
    def _build_control_buttons(self, parent: tk.Widget):
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        self.start_btn = ttk.Button(button_frame, text="启动识别", command=self._on_start_click)
        self.start_btn.pack(fill=tk.X, pady=2)
        self.mouse_btn = ttk.Button(button_frame, text="开启鼠标控制", command=self._on_mouse_click)
        self.mouse_btn.pack(fill=tk.X, pady=2)
        
        self.pause_btn = ttk.Button(button_frame, text="暂停识别", command=self._on_pause_click, state=tk.DISABLED)
        self.pause_btn.pack(fill=tk.X, pady=2)
        self.control_widgets.update({
            'start_btn': self.start_btn,
            'mouse_btn': self.mouse_btn,
            'pause_btn': self.pause_btn
        })
    
    def _build_status_display(self, parent: tk.Widget):
        status_frame = ttk.LabelFrame(parent, text="状态信息", padding="5")
        status_frame.pack(fill=tk.X)       
        # Mouse status
        mouse_frame = ttk.Frame(status_frame)
        mouse_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mouse_frame, text="鼠标控制:", width=12).pack(side=tk.LEFT)
        self.mouse_status_label = ttk.Label(mouse_frame, text="关闭", foreground="red")
        self.mouse_status_label.pack(side=tk.LEFT)
        # Running status
        run_frame = ttk.Frame(status_frame)
        run_frame.pack(fill=tk.X, pady=2)
        ttk.Label(run_frame, text="运行状态:", width=12).pack(side=tk.LEFT)
        self.run_status_label = ttk.Label(run_frame, text="停止", foreground="red")
        self.run_status_label.pack(side=tk.LEFT)
        self.control_widgets.update({
            'mouse_status_label': self.mouse_status_label,
            'run_status_label': self.run_status_label
        })
    
    def _on_start_click(self):
        self.callbacks['start']()
    
    def _on_mouse_click(self):
        self.callbacks['mouse']()
    
    def _on_pause_click(self):
        self.callbacks['pause']()
    
    def update_control_states(self, running: bool):
        if running:
            self.start_btn.config(text="停止识别")
            self.pause_btn.config(state=tk.NORMAL)
        else:
            self.start_btn.config(text="启动识别")
            self.pause_btn.config(state=tk.DISABLED, text="暂停识别")
    
    def update_status(self, status: str, color: str):
        if 'run_status_label' in self.control_widgets:
            self.control_widgets['run_status_label'].config(text=status, foreground=color)
    
    def update_mouse_status(self, enabled: bool):
        if 'mouse_status_label' in self.control_widgets:
            status_text = "开启" if enabled else "关闭"
            color = "green" if enabled else "red"
            self.control_widgets['mouse_status_label'].config(text=status_text, foreground=color)
    
    def _on_resolution_change(self, event=None):
        preset_name = self.config_manager.settings.resolution_preset.get()
        width, height = self.camera_scanner.get_resolution_by_name(preset_name)
        self.config_manager.settings.screen_width.set(width)
        self.config_manager.settings.screen_height.set(height)
        self.resolution_display.config(text=f"{width} x {height}")
            
        print(f"分辨率已更改为: {preset_name} ({width}x{height})")
        
    def _scan_cameras(self):
        self.scan_btn.config(state=tk.DISABLED, text="扫描中...")
        self.camera_status.config(text="正在扫描...")
        import threading
        scan_thread = threading.Thread(target=self._perform_scan, daemon=True)
        scan_thread.start()
        
    def _perform_scan(self):
        try:
            self.available_cameras = self.camera_scanner.scan_cameras()
            self.parent.after(0, self._update_camera_list)
        except Exception as e:
            self.parent.after(0, lambda: self._scan_error(str(e)))
        
    def _update_camera_list(self):
        if self.available_cameras:
            camera_descriptions = [desc for _, desc in self.available_cameras]
            self.camera_combo['values'] = camera_descriptions
            if camera_descriptions:
                self.camera_combo.set(camera_descriptions[0])
                self.camera_combo.current(0)
                self.config_manager.settings.camera_index.set(self.available_cameras[0][0])
                
            self.camera_status.config(text=f"找到 {len(self.available_cameras)} 个摄像头")
        else:
            self.camera_combo['values'] = ["未找到摄像头"]
            self.camera_combo.set("未找到摄像头")
            self.camera_status.config(text="未找到可用摄像头")
            
        self.scan_btn.config(state=tk.NORMAL, text="扫描摄像头")
        
    def _scan_error(self, error_msg):
        self.camera_status.config(text=f"扫描错误: {error_msg}")
        self.scan_btn.config(state=tk.NORMAL, text="扫描摄像头")
        
    def _on_camera_change(self, event=None):
        selection = self.camera_combo.current()
        if 0 <= selection < len(self.available_cameras):
            camera_index = self.available_cameras[selection][0]
            self.config_manager.settings.camera_index.set(camera_index)
            print(f"选择摄像头: {self.available_cameras[selection][1]}")
        
    def _on_cam_resolution_change(self, event=None):
        resolution_str = self.cam_resolution_combo.get()
        try:
            width, height = map(int, resolution_str.split('x'))
            self.config_manager.settings.camera_width.set(width)
            self.config_manager.settings.camera_height.set(height)
            print(f"摄像头分辨率设置为: {width}x{height}")
        except ValueError:
            print(f"无效的分辨率格式: {resolution_str}")
        
    def refresh_display(self):
        settings = self.config_manager.settings
        self.resolution_display.config(
            text=f"{settings.screen_width.get()} x {settings.screen_height.get()}"
        )