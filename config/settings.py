#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tkinter as tk
from typing import Dict, Any, Optional

class Settings:
    
    def __init__(self, root: Optional[tk.Tk] = None):
        self.root = root
        
        self._tk_vars_initialized = False
        self._cached_values = {
            'detection_confidence': 0.7,
            'tracking_confidence': 0.7,
            'pinching_threshold': 0.05,
            'fist_threshold': 0.08,
            'screen_width': 1920,
            'screen_height': 1080,
            'camera_fps': 15,
            'camera_width': 640,
            'camera_height': 480,
            'smoothing_factor': 0.3,
            'scroll_sensitivity': 1.0,
            'camera_index': 0,
            'resolution_preset': '1080p (Full HD)'
        }
        
        self.detection_confidence: Optional[tk.DoubleVar] = None
        self.tracking_confidence: Optional[tk.DoubleVar] = None
        self.pinching_threshold: Optional[tk.DoubleVar] = None
        self.fist_threshold: Optional[tk.DoubleVar] = None
        self.screen_width: Optional[tk.IntVar] = None
        self.screen_height: Optional[tk.IntVar] = None
        self.camera_fps: Optional[tk.IntVar] = None
        self.camera_width: Optional[tk.IntVar] = None
        self.camera_height: Optional[tk.IntVar] = None
        self.smoothing_factor: Optional[tk.DoubleVar] = None
        self.scroll_sensitivity: Optional[tk.DoubleVar] = None
        self.camera_index: Optional[tk.IntVar] = None  # 摄像头索引
        self.resolution_preset: Optional[tk.StringVar] = None  # 分辨率预设
    
    def initialize_tk_vars(self, root: tk.Tk):
        if self._tk_vars_initialized:
            return
            
        self.root = root
        self.detection_confidence = tk.DoubleVar(value=self._cached_values['detection_confidence'])
        self.tracking_confidence = tk.DoubleVar(value=self._cached_values['tracking_confidence'])
        self.pinching_threshold = tk.DoubleVar(value=self._cached_values['pinching_threshold'])
        self.fist_threshold = tk.DoubleVar(value=self._cached_values['fist_threshold'])
        self.screen_width = tk.IntVar(value=self._cached_values['screen_width'])
        self.screen_height = tk.IntVar(value=self._cached_values['screen_height'])
        self.camera_fps = tk.IntVar(value=self._cached_values['camera_fps'])
        self.camera_width = tk.IntVar(value=self._cached_values['camera_width'])
        self.camera_height = tk.IntVar(value=self._cached_values['camera_height'])
        self.smoothing_factor = tk.DoubleVar(value=self._cached_values['smoothing_factor'])
        self.scroll_sensitivity = tk.DoubleVar(value=self._cached_values['scroll_sensitivity'])
        self.camera_index = tk.IntVar(value=self._cached_values['camera_index'])
        self.resolution_preset = tk.StringVar(value=self._cached_values['resolution_preset'])
        
        self._tk_vars_initialized = True
    
    def get_all_values(self) -> Dict[str, Any]:
        if self._tk_vars_initialized:
            return {
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
                'scroll_sensitivity': self.scroll_sensitivity.get(),
                'camera_index': self.camera_index.get(),
                'resolution_preset': self.resolution_preset.get()
            }
        else:
            return self._cached_values.copy()
    
    def set_all_values(self, config_dict: Dict[str, Any]):
        for key, value in config_dict.items():
            if key in self._cached_values:
                self._cached_values[key] = value
        if self._tk_vars_initialized:
            mappings = {
                'detection_confidence': self.detection_confidence,
                'tracking_confidence': self.tracking_confidence,
                'pinching_threshold': self.pinching_threshold,
                'fist_threshold': self.fist_threshold,
                'screen_width': self.screen_width,
                'screen_height': self.screen_height,
                'camera_fps': self.camera_fps,
                'camera_width': self.camera_width,
                'camera_height': self.camera_height,
                'smoothing_factor': self.smoothing_factor,
                'scroll_sensitivity': self.scroll_sensitivity,
                'camera_index': self.camera_index,
                'resolution_preset': self.resolution_preset
            }
            
            for key, var in mappings.items():
                if key in config_dict and var is not None:
                    var.set(config_dict[key])