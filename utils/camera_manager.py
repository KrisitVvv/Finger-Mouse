#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
摄像头管理器类
负责摄像头的初始化、帧捕获和资源释放
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class CameraManager:
    """摄像头管理器类"""
    
    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_initialized = False
        self.camera_index = 0
        self.width = 640
        self.height = 480
        self.fps = 30
    
    def initialize(self, camera_index: int = 0, width: int = 640, 
                   height: int = 480, fps: int = 30) -> bool:
        """
        初始化摄像头
        
        Args:
            camera_index: 摄像头索引
            width: 宽度
            height: 高度
            fps: 帧率
            
        Returns:
            初始化是否成功
        """
        try:
            self.camera_index = camera_index
            self.width = width
            self.height = height
            self.fps = fps
            
            # 创建VideoCapture对象
            self.cap = cv2.VideoCapture(camera_index)
            
            if not self.cap.isOpened():
                print(f"无法打开摄像头 {camera_index}")
                return False
            
            # 设置摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            
            self.is_initialized = True
            print(f"摄像头 {camera_index} 初始化成功 ({width}x{height} @ {fps}fps)")
            return True
            
        except Exception as e:
            print(f"摄像头初始化失败: {e}")
            return False
    
    def reinitialize_with_config(self, config_manager) -> bool:
        """
        根据配置重新初始化摄像头
        
        Args:
            config_manager: 配置管理器
            
        Returns:
            初始化是否成功
        """
        settings = config_manager.get_settings()
        camera_index = settings.camera_index.get() if hasattr(settings.camera_index, 'get') else settings.camera_index
        width = settings.camera_width.get() if hasattr(settings.camera_width, 'get') else settings.camera_width
        height = settings.camera_height.get() if hasattr(settings.camera_height, 'get') else settings.camera_height
        fps = settings.camera_fps.get() if hasattr(settings.camera_fps, 'get') else settings.camera_fps
        
        # 释放现有资源
        self.release()
        
        # 重新初始化
        return self.initialize(camera_index, width, height, fps)
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        获取一帧图像
        
        Returns:
            图像帧，如果失败返回None
        """
        if not self.is_initialized or not self.cap:
            return None
        
        try:
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                return None
        except Exception as e:
            print(f"获取帧时出错: {e}")
            return None
    
    def get_frame_with_status(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        获取帧和状态信息
        
        Returns:
            (是否成功, 图像帧)
        """
        frame = self.get_frame()
        return frame is not None, frame
    
    def set_resolution(self, width: int, height: int) -> bool:
        """设置分辨率"""
        if not self.cap:
            return False
        
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.width = width
            self.height = height
            return True
        except Exception as e:
            print(f"设置分辨率失败: {e}")
            return False
    
    def set_fps(self, fps: int) -> bool:
        """设置帧率"""
        if not self.cap:
            return False
        
        try:
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            self.fps = fps
            return True
        except Exception as e:
            print(f"设置帧率失败: {e}")
            return False
    
    def get_camera_info(self) -> dict:
        """获取摄像头信息"""
        if not self.cap:
            return {}
        
        try:
            return {
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
                'brightness': self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
                'contrast': self.cap.get(cv2.CAP_PROP_CONTRAST),
                'saturation': self.cap.get(cv2.CAP_PROP_SATURATION)
            }
        except Exception:
            return {}
    
    def release(self):
        """释放摄像头资源"""
        try:
            if self.cap:
                self.cap.release()
                self.cap = None
            self.is_initialized = False
            print("摄像头资源已释放")
        except Exception as e:
            print(f"释放摄像头资源时出错: {e}")
    
    def __del__(self):
        """析构函数"""
        self.release()