#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手势识别鼠标控制器测试脚本
用于验证程序各项功能是否正常工作
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def test_imports():
    """测试必要的模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        import cv2
        print("✅ OpenCV 导入成功")
    except ImportError as e:
        print(f"❌ OpenCV 导入失败: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe 导入成功")
        print(f"   版本: {mp.__version__}")
    except ImportError as e:
        print(f"❌ MediaPipe 导入失败: {e}")
        return False
    
    try:
        from pynput import mouse, keyboard
        print("✅ pynput 导入成功")
    except ImportError as e:
        print(f"❌ pynput 导入失败: {e}")
        return False
    
    try:
        from PIL import Image, ImageTk
        print("✅ Pillow 导入成功")
    except ImportError as e:
        print(f"❌ Pillow 导入失败: {e}")
        return False
    
    return True

def test_module_structure():
    """测试模块结构"""
    print("\n🔍 测试模块结构...")
    
    required_modules = [
        'config',
        'gui', 
        'recognition',
        'control',
        'utils'
    ]
    
    required_files = [
        'main.py',
        'config/__init__.py',
        'config/settings.py',
        'config/config_manager.py',
        'gui/__init__.py',
        'gui/main_window.py',
        'gui/controls_panel.py',
        'gui/preview_panel.py',
        'recognition/__init__.py',
        'recognition/hand_detector.py',
        'recognition/gesture_recognizer.py',
        'recognition/gesture_processor.py',
        'control/__init__.py',
        'control/mouse_controller.py',
        'control/keyboard_listener.py',
        'utils/__init__.py',
        'utils/logger.py',
        'utils/camera_manager.py'
    ]
    
    all_good = True
    
    # 检查模块目录
    for module in required_modules:
        if os.path.exists(module) and os.path.isdir(module):
            print(f"✅ 模块目录 {module} 存在")
        else:
            print(f"❌ 模块目录 {module} 不存在")
            all_good = False
    
    # 检查文件
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ 文件 {file_path} 存在")
        else:
            print(f"❌ 文件 {file_path} 不存在")
            all_good = False
    
    return all_good

def test_core_modules():
    """测试核心模块导入"""
    print("\n🔍 测试核心模块导入...")
    
    try:
        # 添加项目根目录到路径
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # 测试配置模块
        from config import Settings, ConfigManager
        print("✅ 配置模块导入成功")
        
        # 测试工具模块
        from utils.logger import setup_logger
        from utils.camera_manager import CameraManager
        print("✅ 工具模块导入成功")
        
        # 测试识别模块
        from recognition import HandDetector, GestureRecognizer
        print("✅ 识别模块导入成功")
        
        # 测试控制模块
        from control import MouseController, KeyboardListener
        print("✅ 控制模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 核心模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_program():
    """测试主程序导入和初始化"""
    print("\n🔍 测试主程序...")
    
    try:
        # 添加当前目录到Python路径
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # 导入主程序模块
        import main
        print("✅ 主程序模块导入成功")
        
        # 创建根窗口（不显示）
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 尝试创建应用实例
        from gui.main_window import MainWindow
        app = MainWindow(root)
        print("✅ 应用实例创建成功")
        
        # 清理
        root.destroy()
        print("✅ 资源清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 主程序测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_camera_access():
    """测试摄像头访问"""
    print("\n🔍 测试摄像头访问...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ 摄像头访问成功")
                print(f"   分辨率: {frame.shape[1]}x{frame.shape[0]}")
                cap.release()
                return True
            else:
                print("❌ 无法读取摄像头帧")
                cap.release()
                return False
        else:
            print("❌ 无法打开摄像头")
            return False
    except Exception as e:
        print(f"❌ 摄像头测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("🖱️ 手势识别鼠标控制器 - 功能测试")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # 测试1: 模块导入
    if test_imports():
        tests_passed += 1
    else:
        print("\n🚨 依赖模块缺失，请安装必要依赖:")
        print("pip install -r requirements.txt")
        return
    
    # 测试2: 模块结构
    if test_module_structure():
        tests_passed += 1
    
    # 测试3: 核心模块
    if test_core_modules():
        tests_passed += 1
    
    # 测试4: 主程序
    if test_main_program():
        tests_passed += 1
    
    # 测试5: 摄像头
    if test_camera_access():
        tests_passed += 1
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {tests_passed}/{total_tests} 项测试通过")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过！程序可以正常使用")
        print("\n💡 使用说明:")
        print("1. 运行: python main.py")
        print("2. 点击'启动识别'开始手势识别")
        print("3. 点击'开启鼠标控制'启用鼠标模拟")
        print("4. 使用手势控制鼠标操作")
    else:
        print("⚠️  部分测试未通过，请检查上述错误信息")
    
    print("=" * 50)

if __name__ == "__main__":
    main()