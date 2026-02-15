#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from datetime import datetime
from typing import Optional
def setup_logger(name: str = __name__, log_file: Optional[str] = None) -> logging.Logger:
    if log_file is None:
        log_filename = f"hand_mouse_{datetime.now().strftime('%Y%m%d')}.log"
        log_file = os.path.join(os.getcwd(), log_filename)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


class LogManager:
    
    def __init__(self, log_file: Optional[str] = None):
        self.logger = setup_logger("HandMouse", log_file)
        self.log_file = log_file or f"hand_mouse_{datetime.now().strftime('%Y%m%d')}.log"
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def get_log_file_path(self) -> str:
        return os.path.abspath(self.log_file)