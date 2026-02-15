#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from typing import Dict, Any, Optional
import tkinter as tk
from .settings import Settings


class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.settings = Settings()
    
    def initialize_with_root(self, root: tk.Tk):
        self.settings.initialize_tk_vars(root)
    
    def save_config(self, filepath: Optional[str] = None) -> bool:
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
        try:
            load_path = filepath or self.config_file
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
        return self.settings
    
    def reset_to_defaults(self):
        self.settings = Settings()