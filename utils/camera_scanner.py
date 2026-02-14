#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
from typing import List, Tuple, Dict
import platform


class CameraScanner:    
    # 常见分辨率预设
    COMMON_RESOLUTIONS = {
        "720p": (1280, 720),
        "1080p (FHD)": (1920, 1080),
        "1440p (2K)": (2560, 1440),
        "2160p (4K)": (3840, 2160),
        "SVGA": (800, 600),
        "XGA": (1024, 768),
        "SXGA": (1280, 1024),
        "UXGA": (1600, 1200)
    }
    
    def __init__(self):
        self.available_cameras: List[Tuple[int, str]] = []
        self.system = platform.system().lower()
    
    def scan_cameras(self, max_ports: int = 10) -> List[Tuple[int, str]]:
        self.available_cameras = []
        
        for port in range(max_ports):
            try:
                cap = cv2.VideoCapture(port)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = int(cap.get(cv2.CAP_PROP_FPS))
                        
                        description = f"摄像头 {port} ({width}x{height} @ {fps}fps)"
                        self.available_cameras.append((port, description))
                
                cap.release()
                
            except Exception as e:
                continue
        
        return self.available_cameras
    
    def get_common_resolutions(self) -> Dict[str, Tuple[int, int]]:
        return self.COMMON_RESOLUTIONS.copy()
    def get_resolution_presets(self) -> List[str]:
        return list(self.COMMON_RESOLUTIONS.keys())
    def get_resolution_by_name(self, name: str) -> Tuple[int, int]:
        return self.COMMON_RESOLUTIONS.get(name, (1920, 1080))
    def test_camera_resolution(self, camera_index: int, width: int, height: int) -> bool:
        try:
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                return False
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            return actual_width == width and actual_height == height
            
        except Exception:
            return False
    
    def get_camera_capabilities(self, camera_index: int) -> Dict[str, any]:
        try:
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                return {}
            
            capabilities = {
                'index': camera_index,
                'supported_resolutions': [],
                'max_fps': int(cap.get(cv2.CAP_PROP_FPS)),
                'brightness': cap.get(cv2.CAP_PROP_BRIGHTNESS),
                'contrast': cap.get(cv2.CAP_PROP_CONTRAST),
                'saturation': cap.get(cv2.CAP_PROP_SATURATION)
            }
            test_resolutions = [
                (640, 480), (800, 600), (1024, 768), 
                (1280, 720), (1280, 1024), (1920, 1080),
                (2560, 1440), (3840, 2160)
            ]
            for width, height in test_resolutions:
                if self.test_camera_resolution(camera_index, width, height):
                    capabilities['supported_resolutions'].append((width, height))
            
            cap.release()
            return capabilities
            
        except Exception as e:
            return {'error': str(e)}