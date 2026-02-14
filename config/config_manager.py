#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置文件管理器
负责配置的保存、加载和验证
"""

import json
import os
from typing import Dict, Any, Optional
import tkinter as tk
from .settings import Settings


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.settings = Settings()
    
    def initialize_with_root(self, root: tk.Tk):
        """使用根窗口初始化TK变量"""
        self.settings.initialize_tk_vars(root)
    
    def save_config(self, filepath: Optional[str] = None) -> bool:
        """保存配置到文件"""
        try:
            config_data = self.settings.get_all_values()
            save_path = filepath or self.config_file
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load_config(self, filepath: Optional[str] = None) -> bool:
        """从文件加载配置"""
        try:
            load_path = filepath or self.config_file
            
            # 如果配置文件不存在，使用默认配置
            if not os.path.exists(load_path):
                return True
            
            with open(load_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.settings.set_all_values(config_data)
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False
    
    def get_settings(self) -> Settings:
        """获取配置设置对象"""
        return self.settings
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        # 重新创建Settings对象以获得默认值
        self.settings = Settings()