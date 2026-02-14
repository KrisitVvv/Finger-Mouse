#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手部检测器类 - 优化版本
负责摄像头管理和手部关键点检测，集成稳定的手势识别，支持骨架数据返回
"""

import cv2
import mediapipe as mp
from typing import Tuple, Optional, Any
import numpy as np

from .gesture_recognizer import GestureRecognizer
from utils.camera_manager import CameraManager


class HandDetector:
    """手部检测器类"""
    
    def __init__(self):
        self._init_mediapipe_components()
        self.camera_manager = CameraManager()
        self.gesture_recognizer = GestureRecognizer()
        self.hands_detector = None
        self.mp_drawing = None
        self.HandLandmark = None
        self.detection_confidence = 0.7
        self.tracking_confidence = 0.7
        self.is_initialized = False
    
    def _init_mediapipe_components(self):
        try:
            import mediapipe as mp
            # 检查API版本
            if hasattr(mp, 'tasks') and hasattr(mp.tasks, 'vision'):
                try:
                    from mediapipe.tasks import vision
                    self.use_new_api = True
                    self.HandLandmarker = vision.HandLandmarker
                    self.HandLandmarkerOptions = vision.HandLandmarkerOptions
                    self.BaseOptions = mp.tasks.BaseOptions
                    self.VisionRunningMode = vision.RunningMode
                except Exception:
                    self.use_new_api = False
            else:
                self.use_new_api = False
            
            # 旧版本API组件
            if not self.use_new_api:
                self.mp_hands = mp.solutions.hands
                self.mp_drawing = mp.solutions.drawing_utils
                self.HandLandmark = self.mp_hands.HandLandmark
                
        except Exception as e:
            raise RuntimeError(f"无法初始化MediaPipe组件: {e}")
    
    def initialize(self, config_manager=None) -> bool:
        """初始化手部检测器"""
        try:
            # 如果提供了配置管理器，使用配置初始化摄像头
            if config_manager:
                if not self.camera_manager.reinitialize_with_config(config_manager):
                    print("摄像头初始化失败")
                    return False
            
            if self.use_new_api:
                result = self._init_new_api_detector()
            else:
                result = self._init_old_api_detector()
            
            if result:
                self.is_initialized = True
            return result
        except Exception as e:
            print(f"初始化手部检测器失败: {e}")
            return False
    
    def _init_new_api_detector(self) -> bool:
        """初始化新版API检测器"""
        try:
            # 这里需要模型文件，暂时回退到旧版API
            print("新版API需要额外的模型文件，使用旧版API")
            return self._init_old_api_detector()
        except Exception as e:
            print(f"新版API初始化失败: {e}")
            return False
    
    def _init_old_api_detector(self) -> bool:
        """初始化旧版API检测器"""
        try:
            # 如果已有检测器，先关闭
            if self.hands_detector:
                try:
                    self.hands_detector.close()
                except:
                    pass
            
            self.hands_detector = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=self.detection_confidence,
                min_tracking_confidence=self.tracking_confidence
            )
            return True
        except Exception as e:
            print(f"旧版API初始化失败: {e}")
            return False
    
    def update_parameters(self, detection_conf: float, tracking_conf: float):
        """更新检测参数"""
        self.detection_confidence = detection_conf
        self.tracking_confidence = tracking_conf
        
        # 重新创建检测器（避免MediaPipe的时间戳问题）
        if self.is_initialized:
            self._reinitialize_detector()
    
    def _reinitialize_detector(self):
        """重新初始化检测器"""
        try:
            # 先清理现有资源
            self.cleanup_detector()
            
            # 重新初始化
            if self.use_new_api:
                self._init_new_api_detector()
            else:
                self._init_old_api_detector()
                
        except Exception as e:
            print(f"重新初始化检测器失败: {e}")
    
    def cleanup_detector(self):
        """清理检测器资源"""
        try:
            if self.hands_detector:
                # 避免MediaPipe的时间戳错误
                try:
                    self.hands_detector.close()
                except Exception:
                    # 如果关闭失败，就让它被垃圾回收
                    pass
                self.hands_detector = None
        except Exception as e:
            print(f"清理检测器时出错: {e}")
    
    def process_frame(self) -> Tuple[Optional[np.ndarray], str, Any]:
        """处理单帧图像并识别手势，返回骨架数据"""
        # 获取摄像头帧
        frame = self.camera_manager.get_frame()
        if frame is None:
            return None, "无", None
        
        # 镜像翻转
        frame = cv2.flip(frame, 1)
        
        if self.use_new_api:
            return self._process_frame_new_api(frame)
        else:
            return self._process_frame_old_api(frame)
    
    def _process_frame_old_api(self, frame: np.ndarray) -> Tuple[np.ndarray, str, Any]:
        """使用旧版API处理帧，返回骨架数据"""
        try:
            # BGR转RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 手部检测
            if not self.hands_detector:
                return frame, "无", None
                
            results = self.hands_detector.process(frame_rgb)
            
            gesture = "无"
            hand_landmarks = None
            
            # 如果检测到手部
            if results.multi_hand_landmarks:
                # 使用第一个检测到的手
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # 识别手势 - 使用优化后的识别器
                gesture = self.gesture_recognizer.recognize_gesture(hand_landmarks)
            
            return frame, gesture, hand_landmarks
            
        except Exception as e:
            print(f"帧处理出错: {e}")
            return frame, "无", None
    
    def _process_frame_new_api(self, frame: np.ndarray) -> Tuple[np.ndarray, str, Any]:
        """使用新版API处理帧（占位实现）"""
        # 新版API需要额外的实现
        return frame, "无", None
    
    def cleanup(self):
        """清理所有资源"""
        try:
            self.cleanup_detector()
            self.camera_manager.release()
            self.gesture_recognizer.reset_stability()  # 重置手势识别稳定性
            self.is_initialized = False
        except Exception as e:
            print(f"清理资源时出错: {e}")
    
    def update_gesture_thresholds(self, pinch=None, fist=None, click_contact=None, finger_proximity=None):
        """更新手势识别阈值"""
        self.gesture_recognizer.update_thresholds(pinch, fist, click_contact, finger_proximity)