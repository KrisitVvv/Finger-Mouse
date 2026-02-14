import cv2
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key
import json
import os
import logging
from datetime import datetime

# 新版MediaPipe API兼容性处理
USE_NEW_API = False  # 全局变量，初始化为False

class HandMouseControllerGUI:
    def __init__(self, root):
        # 主窗口配置
        self.root = root
        self.root.title("Windows 手势识别鼠标控制器")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # 日志配置
        self._setup_logging()
        
        # 核心状态变量
        self.is_running = False  # 识别线程是否运行
        self.mouse_control_enabled = False  # 是否启用鼠标模拟
        self.recognize_thread = None  # 识别线程
        self.keyboard_listener = None  # 键盘监听器
        self.is_paused = False  # 是否暂停识别
        
        # 配置参数变量
        self.detection_confidence = tk.DoubleVar(value=0.7)
        self.tracking_confidence = tk.DoubleVar(value=0.7)
        self.pinching_threshold = tk.DoubleVar(value=0.05)
        self.fist_threshold = tk.DoubleVar(value=0.08)
        self.screen_width = tk.IntVar(value=1920)
        self.screen_height = tk.IntVar(value=1080)
        self.camera_fps = tk.IntVar(value=15)
        self.camera_width = tk.IntVar(value=640)
        self.camera_height = tk.IntVar(value=480)
        self.smoothing_factor = tk.DoubleVar(value=0.3)
        self.scroll_sensitivity = tk.DoubleVar(value=1.0)
        
        # 手势状态变量
        self.current_gesture = "无"
        self.previous_gesture = "无"
        self.gesture_timestamp = time.time()
        self.mouse_pressed = False
        self.right_click_ready = False
        
        # 初始化核心组件
        self.mouse = Controller()
        
        # 初始化MediaPipe组件
        self._init_mediapipe_components()
        
        # 根据API版本初始化手部检测器
        if USE_NEW_API:
            self._init_new_api_detector()
        else:
            self._init_old_api_detector()
            
        self.cap = None  # 摄像头对象
        self.frame_buffer = []  # 帧缓冲用于平滑处理
        
        # 上次鼠标位置（用于移动计算）
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        # 构建GUI界面
        self._build_gui()
        
        # 加载配置
        self._load_config()
        
        # 窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 启动键盘监听
        self._start_keyboard_listener()

    def _init_new_api_detector(self):
        """初始化新版MediaPipe API检测器"""
        try:
            # 创建手部标记器选项
            base_options = BaseOptions(model_asset_path='hand_landmarker.task')  # 需要下载模型文件
            options = HandLandmarkerOptions(
                base_options=base_options,
                running_mode=VisionRunningMode.LIVE_STREAM,
                num_hands=1,
                min_hand_detection_confidence=self.detection_confidence.get(),
                min_hand_presence_confidence=self.tracking_confidence.get(),
                result_callback=self._hand_landmark_callback
            )
            self.hands = HandLandmarker.create_from_options(options)
            self.new_api_results = None
        except Exception as e:
            self.logger.warning(f"新版API初始化失败，回退到旧版API: {e}")
            global USE_NEW_API
            USE_NEW_API = False
            self._init_old_api_detector()

    def _init_mediapipe_components(self):
        """初始化MediaPipe核心组件"""
        global USE_NEW_API
        try:
            import mediapipe as mp
            
            # 检查API版本
            if hasattr(mp, 'tasks') and hasattr(mp.tasks, 'vision'):
                # 尝试新版API
                try:
                    from mediapipe.tasks import vision
                    USE_NEW_API = True
                    self.HandLandmarker = vision.HandLandmarker
                    self.HandLandmarkerOptions = vision.HandLandmarkerOptions
                    self.BaseOptions = mp.tasks.BaseOptions
                    self.VisionRunningMode = vision.RunningMode
                    self.logger.info("新版API组件初始化成功")
                except Exception as e:
                    self.logger.warning(f"新版API初始化失败: {e}")
                    USE_NEW_API = False
            
            # 初始化旧版API组件（总是需要）
            if not USE_NEW_API:
                self.mp_hands = mp.solutions.hands
                self.mp_drawing = mp.solutions.drawing_utils
                self.HandLandmark = self.mp_hands.HandLandmark
                self.logger.info("旧版API组件初始化成功")
                
        except Exception as e:
            self.logger.error(f"MediaPipe组件初始化失败: {e}")
            raise RuntimeError(f"无法初始化MediaPipe: {e}")

    def _init_old_api_detector(self):
        """初始化旧版MediaPipe API检测器"""
        try:
            self.logger.info("正在初始化旧版MediaPipe API...")
            self.hands = self._create_hands_detector()
            self.logger.info("旧版API初始化成功")
        except Exception as e:
            error_msg = f"无法初始化手部检测器: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _hand_landmark_callback(self, result, output_image, timestamp_ms):
        """新版API的回调函数"""
        self.new_api_results = result

    def _create_hands_detector(self):
        """创建MediaPipe Hands检测器（旧版API）"""
        try:
            self.logger.info("正在创建手部检测器...")
            self.logger.info(f"检测置信度: {self.detection_confidence.get()}")
            self.logger.info(f"跟踪置信度: {self.tracking_confidence.get()}")
            
            detector = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=self.detection_confidence.get(),
                min_tracking_confidence=self.tracking_confidence.get()
            )
            self.logger.info("手部检测器创建成功")
            return detector
        except Exception as e:
            error_msg = f"创建手势检测器失败: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(f"参数详情 - 检测置信度: {self.detection_confidence.get()}, 跟踪置信度: {self.tracking_confidence.get()}")
            raise Exception(error_msg)

    def _recognize_loop(self):
        """手势识别主循环"""
        global USE_NEW_API
        if USE_NEW_API:
            self._recognize_loop_new_api()
        else:
            self._recognize_loop_old_api()

    def _recognize_loop_old_api(self):
        """旧版API识别循环"""
        while self.is_running:
            if self.is_paused or not self.cap or not self.cap.isOpened():
                time.sleep(0.1)
                continue
            
            try:
                success, frame = self.cap.read()
                if not success:
                    time.sleep(0.1)
                    continue
                
                # 帧预处理：BGR转RGB，镜像翻转
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(frame_rgb)
                
                self.current_gesture = "无"
                
                # 识别到手部
                if results.multi_hand_landmarks:
                    for hand_lm in results.multi_hand_landmarks:
                        # 绘制手部关键点
                        self.mp_drawing.draw_landmarks(
                            frame, hand_lm, self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                            self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=1)
                        )
                        
                        # 手势判断
                        if self._is_ok_sign_old(hand_lm):
                            self.current_gesture = "OK手势"
                            if self.previous_gesture != "OK手势":
                                self._toggle_pause()
                                
                        elif self._is_victory_sign_old(hand_lm):
                            self.current_gesture = "V字手势"
                            if self.mouse_control_enabled and not self.right_click_ready:
                                self.mouse.click(Button.right)
                                self.right_click_ready = True
                                
                        elif self._is_pinching_old(hand_lm):
                            self.current_gesture = "捏合"
                            if self.mouse_control_enabled:
                                cx, cy = self._get_hand_center_old(hand_lm)
                                smooth_cx, smooth_cy = self._smooth_coordinates(cx, cy)
                                mouse_x = smooth_cx * self.screen_width.get()
                                mouse_y = smooth_cy * self.screen_height.get()
                                self.mouse.position = (mouse_x, mouse_y)
                                
                                if self.mouse_pressed:
                                    self.mouse.release(Button.left)
                                    self.mouse_pressed = False
                                    
                        elif self._is_fist_old(hand_lm):
                            self.current_gesture = "握拳"
                            if self.mouse_control_enabled and not self.mouse_pressed:
                                self.mouse.press(Button.left)
                                self.mouse_pressed = True
                                
                        else:
                            self.current_gesture = "手掌张开"
                            if self.mouse_control_enabled and self.mouse_pressed:
                                self.mouse.release(Button.left)
                                self.mouse_pressed = False
                        
                        if self.current_gesture != "V字手势" and self.right_click_ready:
                            self.right_click_ready = False
                
                # 更新预览画面
                self._update_preview(frame)
                self._update_gesture_display()
                time.sleep(1/max(1, self.camera_fps.get()))
                
            except Exception as e:
                self.logger.error(f"识别循环出错: {e}")
                time.sleep(0.1)

    def _recognize_loop_new_api(self):
        """新版API识别循环"""
        # 注意：新版API需要模型文件，这里暂时回退到旧版API
        self.logger.info("新版API需要额外的模型文件，暂时使用旧版API")
        global USE_NEW_API
        USE_NEW_API = False
        self._recognize_loop_old_api()

    # 旧版API的手势检测方法
    def _is_pinching_old(self, hand_landmarks):
        """判断是否为捏合手势（拇指+食指）"""
        try:
            thumb_tip = hand_landmarks.landmark[self.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[self.HandLandmark.INDEX_FINGER_TIP]
            distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
            return distance < self.pinching_threshold.get()
        except Exception as e:
            self.logger.error(f"捏合检测出错: {e}")
            return False

    def _is_fist_old(self, hand_landmarks):
        """判断是否为握拳手势"""
        try:
            palm_base = hand_landmarks.landmark[self.HandLandmark.WRIST]
            finger_tips = [
                self.HandLandmark.THUMB_TIP,
                self.HandLandmark.INDEX_FINGER_TIP,
                self.HandLandmark.MIDDLE_FINGER_TIP,
                self.HandLandmark.RING_FINGER_TIP,
                self.HandLandmark.PINKY_TIP
            ]
            for tip in finger_tips:
                distance = ((hand_landmarks.landmark[tip].x - palm_base.x)**2 + 
                           (hand_landmarks.landmark[tip].y - palm_base.y)**2)**0.5
                if distance > self.fist_threshold.get():
                    return False
            return True
        except Exception as e:
            self.logger.error(f"握拳检测出错: {e}")
            return False

    def _is_victory_sign_old(self, hand_landmarks):
        """判断V字手势（食指+中指伸直）"""
        try:
            index_tip = hand_landmarks.landmark[self.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[self.HandLandmark.MIDDLE_FINGER_TIP]
            wrist = hand_landmarks.landmark[self.HandLandmark.WRIST]
            ring_tip = hand_landmarks.landmark[self.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[self.HandLandmark.PINKY_TIP]
            
            index_extended = index_tip.y < wrist.y
            middle_extended = middle_tip.y < wrist.y
            others_bent = (ring_tip.y > wrist.y) and (pinky_tip.y > wrist.y)
            
            return index_extended and middle_extended and others_bent
        except Exception as e:
            self.logger.error(f"V字手势检测出错: {e}")
            return False

    def _is_ok_sign_old(self, hand_landmarks):
        """判断OK手势（拇指和食指形成圆圈）"""
        try:
            thumb_tip = hand_landmarks.landmark[self.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[self.HandLandmark.INDEX_FINGER_TIP]
            distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
            return distance < 0.03
        except Exception as e:
            self.logger.error(f"OK手势检测出错: {e}")
            return False

    def _get_hand_center_old(self, hand_landmarks):
        """计算手部中心坐标"""
        try:
            x_sum, y_sum = 0, 0
            for lm in hand_landmarks.landmark:
                x_sum += lm.x
                y_sum += lm.y
            return x_sum/21, y_sum/21
        except Exception as e:
            self.logger.error(f"计算手部中心出错: {e}")
            return 0.5, 0.5

    def _smooth_coordinates(self, x, y):
        """平滑坐标值"""
        if not self.frame_buffer:
            self.frame_buffer = [(x, y)] * 5  # 初始化缓冲区
        
        # 添加新坐标到缓冲区
        self.frame_buffer.append((x, y))
        if len(self.frame_buffer) > 5:
            self.frame_buffer.pop(0)
        
        # 计算平均值
        avg_x = sum(pos[0] for pos in self.frame_buffer) / len(self.frame_buffer)
        avg_y = sum(pos[1] for pos in self.frame_buffer) / len(self.frame_buffer)
        
        # 应用平滑因子
        smooth_x = self.last_mouse_x * (1 - self.smoothing_factor.get()) + avg_x * self.smoothing_factor.get()
        smooth_y = self.last_mouse_y * (1 - self.smoothing_factor.get()) + avg_y * self.smoothing_factor.get()
        
        self.last_mouse_x, self.last_mouse_y = smooth_x, smooth_y
        return smooth_x, smooth_y

    def _update_preview(self, frame):
        """更新预览画面"""
        try:
            # 转换为PhotoImage格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 居中显示
                x_offset = (canvas_width - new_width) // 2
                y_offset = (canvas_height - new_height) // 2
                
                photo = ImageTk.PhotoImage(img)
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo)
                self.preview_canvas.image = photo  # 保持引用
                
        except Exception as e:
            self.logger.error(f"更新预览出错: {e}")

    def _update_gesture_display(self):
        """更新手势显示"""
        try:
            self.gesture_label.config(text=self.current_gesture)
            
            # 不同手势不同颜色
            color_map = {
                "无": "gray",
                "捏合": "blue",
                "握拳": "red",
                "手掌张开": "green",
                "V字手势": "purple",
                "OK手势": "orange"
            }
            color = color_map.get(self.current_gesture, "black")
            self.gesture_label.config(foreground=color)
            
            # 更新全局状态
            self.previous_gesture = self.current_gesture
            
        except Exception as e:
            self.logger.error(f"更新手势显示出错: {e}")

    def _update_status(self, status, color):
        """更新运行状态显示"""
        try:
            self.run_status_label.config(text=status, foreground=color)
            # 更新状态栏
            mouse_status = "开启" if self.mouse_control_enabled else "关闭"
            pause_status = "暂停" if self.is_paused else "运行"
            self.status_bar.config(text=f"状态: {status} | 手势: {self.current_gesture} | 鼠标: {mouse_status} | {pause_status}")
        except Exception as e:
            self.logger.error(f"更新状态出错: {e}")

    def _setup_logging(self):
        """设置日志记录"""
        log_filename = f"hand_mouse_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _build_gui(self):
        """构建GUI布局"""
        # 创建菜单栏
        self._create_menu()
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 参数设置区域
        self._build_parameter_controls(control_frame)
        
        # 控制按钮区域
        self._build_control_buttons(control_frame)
        
        # 右侧预览和状态区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 摄像头预览区域
        self._build_preview_area(right_frame)
        
        # 状态信息区域
        self._build_status_area(right_frame)
        
        # 底部状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

    # ... 其他GUI构建方法保持不变 ...

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
        setting_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=setting_menu)
        setting_menu.add_command(label="热键设置", command=self._show_hotkey_settings)
        setting_menu.add_command(label="手势映射", command=self._show_gesture_mapping)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)

    def _build_parameter_controls(self, parent):
        """构建参数控制区域"""
        param_frame = ttk.LabelFrame(parent, text="参数设置", padding="5")
        param_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 识别参数
        ttk.Label(param_frame, text="检测置信度:").grid(row=0, column=0, sticky=tk.W, pady=2)
        detection_slider = ttk.Scale(param_frame, from_=0.5, to=0.9, variable=self.detection_confidence,
                                   command=lambda v: self._update_hands_detector())
        detection_slider.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=self.detection_confidence).grid(row=0, column=2, padx=5)
        
        ttk.Label(param_frame, text="跟踪置信度:").grid(row=1, column=0, sticky=tk.W, pady=2)
        tracking_slider = ttk.Scale(param_frame, from_=0.5, to=0.9, variable=self.tracking_confidence,
                                  command=lambda v: self._update_hands_detector())
        tracking_slider.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=self.tracking_confidence).grid(row=1, column=2, padx=5)
        
        # 手势阈值
        ttk.Label(param_frame, text="捏合阈值:").grid(row=2, column=0, sticky=tk.W, pady=2)
        pinching_slider = ttk.Scale(param_frame, from_=0.01, to=0.1, variable=self.pinching_threshold)
        pinching_slider.grid(row=2, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=self.pinching_threshold).grid(row=2, column=2, padx=5)
        
        ttk.Label(param_frame, text="握拳阈值:").grid(row=3, column=0, sticky=tk.W, pady=2)
        fist_slider = ttk.Scale(param_frame, from_=0.05, to=0.15, variable=self.fist_threshold)
        fist_slider.grid(row=3, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=self.fist_threshold).grid(row=3, column=2, padx=5)
        
        # 平滑参数
        ttk.Label(param_frame, text="平滑因子:").grid(row=4, column=0, sticky=tk.W, pady=2)
        smoothing_slider = ttk.Scale(param_frame, from_=0.1, to=0.8, variable=self.smoothing_factor)
        smoothing_slider.grid(row=4, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=self.smoothing_factor).grid(row=4, column=2, padx=5)
        
        ttk.Label(param_frame, text="滚动灵敏度:").grid(row=5, column=0, sticky=tk.W, pady=2)
        scroll_slider = ttk.Scale(param_frame, from_=0.5, to=2.0, variable=self.scroll_sensitivity)
        scroll_slider.grid(row=5, column=1, padx=5, pady=2, sticky=tk.EW)
        ttk.Label(param_frame, textvariable=self.scroll_sensitivity).grid(row=5, column=2, padx=5)
        
        # 屏幕参数
        screen_frame = ttk.LabelFrame(parent, text="屏幕设置", padding="5")
        screen_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(screen_frame, text="屏幕宽度:").grid(row=0, column=0, sticky=tk.W, pady=2)
        width_entry = ttk.Entry(screen_frame, textvariable=self.screen_width, width=10)
        width_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(screen_frame, text="屏幕高度:").grid(row=1, column=0, sticky=tk.W, pady=2)
        height_entry = ttk.Entry(screen_frame, textvariable=self.screen_height, width=10)
        height_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # 摄像头参数
        camera_frame = ttk.LabelFrame(parent, text="摄像头设置", padding="5")
        camera_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(camera_frame, text="帧率:").grid(row=0, column=0, sticky=tk.W, pady=2)
        fps_entry = ttk.Entry(camera_frame, textvariable=self.camera_fps, width=10)
        fps_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(camera_frame, text="宽度:").grid(row=1, column=0, sticky=tk.W, pady=2)
        cam_w_entry = ttk.Entry(camera_frame, textvariable=self.camera_width, width=10)
        cam_w_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(camera_frame, text="高度:").grid(row=2, column=0, sticky=tk.W, pady=2)
        cam_h_entry = ttk.Entry(camera_frame, textvariable=self.camera_height, width=10)
        cam_h_entry.grid(row=2, column=1, padx=5, pady=2)

    def _build_control_buttons(self, parent):
        """构建控制按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=5)
        
        # 主要控制按钮
        self.start_btn = ttk.Button(button_frame, text="启动识别", command=self._toggle_recognition)
        self.start_btn.pack(fill=tk.X, pady=2)
        
        self.mouse_btn = ttk.Button(button_frame, text="开启鼠标控制", command=self._toggle_mouse_control)
        self.mouse_btn.pack(fill=tk.X, pady=2)
        
        self.pause_btn = ttk.Button(button_frame, text="暂停识别", command=self._toggle_pause, state=tk.DISABLED)
        self.pause_btn.pack(fill=tk.X, pady=2)
        
        # 测试按钮
        test_frame = ttk.LabelFrame(parent, text="测试功能", padding="5")
        test_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(test_frame, text="测试鼠标移动", command=self._test_mouse_move).pack(fill=tk.X, pady=1)
        ttk.Button(test_frame, text="测试左键点击", command=self._test_left_click).pack(fill=tk.X, pady=1)
        ttk.Button(test_frame, text="测试右键点击", command=self._test_right_click).pack(fill=tk.X, pady=1)

    def _build_preview_area(self, parent):
        """构建预览区域"""
        preview_frame = ttk.LabelFrame(parent, text="摄像头预览", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建画布用于显示图像
        self.preview_canvas = tk.Canvas(preview_frame, bg='black')
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 添加预览控制
        preview_ctrl_frame = ttk.Frame(preview_frame)
        preview_ctrl_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(preview_ctrl_frame, text="截图保存", command=self._save_screenshot).pack(side=tk.LEFT, padx=2)
        ttk.Button(preview_ctrl_frame, text="刷新摄像头", command=self._refresh_camera).pack(side=tk.LEFT, padx=2)

    def _build_status_area(self, parent):
        """构建状态显示区域"""
        status_frame = ttk.LabelFrame(parent, text="状态信息", padding="5")
        status_frame.pack(fill=tk.X)
        
        # 手势状态
        gesture_frame = ttk.Frame(status_frame)
        gesture_frame.pack(fill=tk.X, pady=2)
        ttk.Label(gesture_frame, text="当前手势:", width=12).pack(side=tk.LEFT)
        self.gesture_label = ttk.Label(gesture_frame, text="无", foreground="blue")
        self.gesture_label.pack(side=tk.LEFT)
        
        # 鼠标状态
        mouse_frame = ttk.Frame(status_frame)
        mouse_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mouse_frame, text="鼠标控制:", width=12).pack(side=tk.LEFT)
        self.mouse_status_label = ttk.Label(mouse_frame, text="关闭", foreground="red")
        self.mouse_status_label.pack(side=tk.LEFT)
        
        # 运行状态
        run_frame = ttk.Frame(status_frame)
        run_frame.pack(fill=tk.X, pady=2)
        ttk.Label(run_frame, text="运行状态:", width=12).pack(side=tk.LEFT)
        self.run_status_label = ttk.Label(run_frame, text="停止", foreground="red")
        self.run_status_label.pack(side=tk.LEFT)

    def _update_hands_detector(self):
        """更新MediaPipe Hands检测器参数"""
        if hasattr(self, 'hands') and self.hands:
            self.hands.close()
        self.hands = self._create_hands_detector()

    def _toggle_recognition(self):
        """启动/暂停手势识别"""
        if not self.is_running:
            self._start_recognition()
        else:
            self._stop_recognition()

    def _start_recognition(self):
        """启动识别"""
        try:
            # 初始化摄像头
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("错误", "无法打开摄像头，请检查设备连接")
                return
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width.get())
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height.get())
            self.cap.set(cv2.CAP_PROP_FPS, self.camera_fps.get())
            
            # 启动识别线程
            self.is_running = True
            self.is_paused = False
            self.start_btn.config(text="停止识别")
            self.pause_btn.config(state=tk.NORMAL)
            
            self.recognize_thread = threading.Thread(target=self._recognize_loop, daemon=True)
            self.recognize_thread.start()
            
            self._update_status("运行中", "green")
            self.logger.info("手势识别已启动")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动识别失败: {e}")
            self.logger.error(f"启动识别失败: {e}")

    def _stop_recognition(self):
        """停止识别"""
        self.is_running = False
        self.is_paused = False
        
        # 释放摄像头
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.start_btn.config(text="启动识别")
        self.pause_btn.config(state=tk.DISABLED, text="暂停识别")
        self._update_status("已停止", "red")
        self.logger.info("手势识别已停止")

    def _toggle_pause(self):
        """暂停/恢复识别"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="恢复识别")
            self._update_status("已暂停", "orange")
            self.logger.info("识别已暂停")
        else:
            self.pause_btn.config(text="暂停识别")
            self._update_status("运行中", "green")
            self.logger.info("识别已恢复")

    def _toggle_mouse_control(self):
        """开启/关闭鼠标模拟"""
        self.mouse_control_enabled = not self.mouse_control_enabled
        if self.mouse_control_enabled:
            self.mouse_btn.config(text="关闭鼠标控制")
            self.mouse_status_label.config(text="开启", foreground="green")
            self.logger.info("鼠标控制已开启")
        else:
            self.mouse_btn.config(text="开启鼠标控制")
            self.mouse_status_label.config(text="关闭", foreground="red")
            # 释放可能按下的鼠标按键
            if self.mouse_pressed:
                self.mouse.release(Button.left)
                self.mouse_pressed = False
            self.logger.info("鼠标控制已关闭")

    def _start_keyboard_listener(self):
        """启动键盘监听器"""
        def on_press(key):
            try:
                # Ctrl+Alt+G 切换识别状态
                if hasattr(key, 'char') and key.char == 'g':
                    if hasattr(self, '_ctrl_pressed') and hasattr(self, '_alt_pressed'):
                        if self._ctrl_pressed and self._alt_pressed:
                            self.root.after(0, self._toggle_recognition)
                            
                # 记录修饰键状态
                if key == Key.ctrl_l or key == Key.ctrl_r:
                    self._ctrl_pressed = True
                elif key == Key.alt_l or key == Key.alt_r:
                    self._alt_pressed = True
                    
            except Exception as e:
                self.logger.error(f"键盘监听出错: {e}")

        def on_release(key):
            try:
                # 释放修饰键状态
                if key == Key.ctrl_l or key == Key.ctrl_r:
                    self._ctrl_pressed = False
                elif key == Key.alt_l or key == Key.alt_r:
                    self._alt_pressed = False
                    
            except Exception as e:
                self.logger.error(f"键盘释放监听出错: {e}")

        try:
            self.keyboard_listener = Listener(on_press=on_press, on_release=on_release)
            self.keyboard_listener.start()
            self.logger.info("键盘监听器已启动")
        except Exception as e:
            self.logger.error(f"启动键盘监听器失败: {e}")

    # 测试功能方法
    def _test_mouse_move(self):
        """测试鼠标移动"""
        try:
            current_x, current_y = self.mouse.position
            self.mouse.move(50, 50)
            self.logger.info(f"鼠标移动测试: ({current_x}, {current_y}) -> ({current_x+50}, {current_y+50})")
        except Exception as e:
            messagebox.showerror("错误", f"鼠标移动测试失败: {e}")

    def _test_left_click(self):
        """测试左键点击"""
        try:
            self.mouse.click(Button.left)
            self.logger.info("左键点击测试")
        except Exception as e:
            messagebox.showerror("错误", f"左键点击测试失败: {e}")

    def _test_right_click(self):
        """测试右键点击"""
        try:
            self.mouse.click(Button.right)
            self.logger.info("右键点击测试")
        except Exception as e:
            messagebox.showerror("错误", f"右键点击测试失败: {e}")

    def _save_screenshot(self):
        """保存当前预览截图"""
        try:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    messagebox.showinfo("成功", f"截图已保存为: {filename}")
                    self.logger.info(f"截图已保存: {filename}")
                else:
                    messagebox.showerror("错误", "无法获取当前帧")
            else:
                messagebox.showerror("错误", "摄像头未启动")
        except Exception as e:
            messagebox.showerror("错误", f"保存截图失败: {e}")

    def _refresh_camera(self):
        """刷新摄像头连接"""
        try:
            if self.is_running:
                # 重新初始化摄像头
                if self.cap:
                    self.cap.release()
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width.get())
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height.get())
                self.cap.set(cv2.CAP_PROP_FPS, self.camera_fps.get())
                self.logger.info("摄像头已刷新")
            else:
                messagebox.showinfo("提示", "请先启动识别")
        except Exception as e:
            messagebox.showerror("错误", f"刷新摄像头失败: {e}")

    # 配置管理方法
    def _save_config(self):
        """保存配置到文件"""
        try:
            config = {
                'detection_confidence': self.detection_confidence.get(),
                'tracking_confidence': self.tracking_confidence.get(),
                'pinching_threshold': self.pinching_threshold.get(),
                'fist_threshold': self.fist_threshold.get(),
                'screen_width': self.screen_width.get(),
                'screen_height': self.screen_height.get(),
                'camera_fps': self.camera_fps.get(),
                'camera_width': self.camera_width.get(),
                'camera_height': self.camera_height.get(),
                'smoothing_factor': self.smoothing_factor.get(),
                'scroll_sensitivity': self.scroll_sensitivity.get()
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", f"配置已保存到: {filename}")
                self.logger.info(f"配置已保存: {filename}")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")

    def _load_config(self, filename=None):
        """从文件加载配置"""
        try:
            if not filename:
                filename = "config.json"
                if not os.path.exists(filename):
                    return  # 使用默认配置
                    
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新变量
            self.detection_confidence.set(config.get('detection_confidence', 0.7))
            self.tracking_confidence.set(config.get('tracking_confidence', 0.7))
            self.pinching_threshold.set(config.get('pinching_threshold', 0.05))
            self.fist_threshold.set(config.get('fist_threshold', 0.08))
            self.screen_width.set(config.get('screen_width', 1920))
            self.screen_height.set(config.get('screen_height', 1080))
            self.camera_fps.set(config.get('camera_fps', 15))
            self.camera_width.set(config.get('camera_width', 640))
            self.camera_height.set(config.get('camera_height', 480))
            self.smoothing_factor.set(config.get('smoothing_factor', 0.3))
            self.scroll_sensitivity.set(config.get('scroll_sensitivity', 1.0))
            
            # 更新检测器
            self._update_hands_detector()
            
            self.logger.info(f"配置已加载: {filename}")
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")

    def _load_config_dialog(self):
        """通过对话框加载配置"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                self._load_config(filename)
                messagebox.showinfo("成功", f"配置已从 {filename} 加载")
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {e}")

    # 对话框方法
    def _show_hotkey_settings(self):
        """显示热键设置对话框"""
        messagebox.showinfo("热键设置", "当前支持的热键:\nCtrl+Alt+G: 启动/停止识别")

    def _show_gesture_mapping(self):
        """显示手势映射对话框"""
        mapping_text = """
手势映射说明:
• 捏合手势: 鼠标移动
• 握拳: 鼠标左键按下
• 张开手掌: 鼠标左键释放
• V字手势: 鼠标右键点击
• OK手势: 暂停/恢复识别
        """
        messagebox.showinfo("手势映射", mapping_text)

    def _show_help(self):
        """显示帮助信息"""
        help_text = """
使用说明:
1. 点击"启动识别"开始手势识别
2. 点击"开启鼠标控制"启用鼠标模拟
3. 使用不同手势控制鼠标:
   - 捏合: 移动鼠标
   - 握拳: 按下左键
   - 张开: 释放左键
   - V字: 右键点击
   - OK: 暂停/恢复
4. 可通过参数面板调整识别灵敏度
5. 支持热键 Ctrl+Alt+G 切换识别状态
        """
        messagebox.showinfo("使用帮助", help_text)

    def _show_about(self):
        """显示关于信息"""
        about_text = """
手势识别鼠标控制器 v1.0

基于 MediaPipe 和 OpenCV 的手势识别系统
支持多种手势控制鼠标操作

作者: AI Assistant
开发语言: Python
        """
        messagebox.showinfo("关于", about_text)

    def _on_close(self):
        """关闭程序时释放资源"""
        try:
            self.logger.info("程序正在关闭...")
            
            # 停止识别
            self.is_running = False
            self.is_paused = False
            
            # 释放摄像头
            if self.cap:
                self.cap.release()
                
            # 关闭手势检测器
            if hasattr(self, 'hands') and self.hands:
                self.hands.close()
                
            # 停止键盘监听
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                
            # 释放鼠标按键
            if self.mouse_pressed:
                self.mouse.release(Button.left)
                
            # 清理OpenCV窗口
            cv2.destroyAllWindows()
            
            self.logger.info("资源已释放，程序退出")
            self.root.quit()
            
        except Exception as e:
            self.logger.error(f"关闭程序时出错: {e}")
            self.root.destroy()

if __name__ == "__main__":
    # 检查依赖
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import mediapipe
    except ImportError:
        missing_deps.append("mediapipe")
    
    try:
        from pynput import mouse, keyboard
    except ImportError:
        missing_deps.append("pynput")
    
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("pillow")
    
    if missing_deps:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        deps_str = ", ".join(missing_deps)
        install_cmd = f"pip install {' '.join(missing_deps)}"
        messagebox.showerror("依赖缺失", 
                           f"缺少必要依赖：{deps_str}\n\n请运行以下命令安装：\n{install_cmd}")
        root.destroy()
    else:
        try:
            root = tk.Tk()
            app = HandMouseControllerGUI(root)
            root.mainloop()
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("程序错误", f"程序启动失败：{str(e)}")
            root.destroy()