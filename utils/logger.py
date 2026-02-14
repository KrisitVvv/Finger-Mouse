#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志工具类
负责程序日志记录和管理
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(name: str = __name__, log_file: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径，如果为None则自动生成
    
    Returns:
        配置好的日志记录器
    """
    # 如果没有指定日志文件，生成带日期的文件名
    if log_file is None:
        log_filename = f"hand_mouse_{datetime.now().strftime('%Y%m%d')}.log"
        log_file = os.path.join(os.getcwd(), log_filename)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 设置格式器
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


class LogManager:
    """日志管理器类"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.logger = setup_logger("HandMouse", log_file)
        self.log_file = log_file or f"hand_mouse_{datetime.now().strftime('%Y%m%d')}.log"
    
    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)
    
    def get_log_file_path(self) -> str:
        """获取日志文件路径"""
        return os.path.abspath(self.log_file)