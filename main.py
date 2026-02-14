#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手势识别鼠标控制器 - 主程序入口
基于 MediaPipe 和 OpenCV 的手势识别系统
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查必要的依赖包"""
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
        error_msg = "缺少必要依赖包:\n" + "\n".join(f"- {dep}" for dep in missing_deps)
        install_cmd = f"pip install {' '.join(missing_deps)}"
        print(error_msg)
        print(f"\n请运行以下命令安装:\n{install_cmd}")
        return False
    
    return True

def main():
    """主函数"""
    # 检查依赖
    if not check_dependencies():
        input("按回车键退出...")
        return
    
    try:
        # 导入GUI模块
        from gui.main_window import MainWindow
        
        # 创建根窗口
        root = tk.Tk()
        
        # 创建主应用窗口
        app = MainWindow(root)
        
        # 启动GUI主循环
        root.mainloop()
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()