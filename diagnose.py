#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最基本的手势识别诊断脚本
"""

print("Starting diagnosis...")

# 测试基本导入
try:
    import cv2
    print("✓ OpenCV imported")
except ImportError as e:
    print(f"✗ OpenCV import failed: {e}")

try:
    import mediapipe as mp
    print("✓ MediaPipe imported")
except ImportError as e:
    print(f"✗ MediaPipe import failed: {e}")

try:
    import numpy as np
    print("✓ NumPy imported")
except ImportError as e:
    print(f"✗ NumPy import failed: {e}")

# 测试MediaPipe初始化
try:
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
    print("✓ MediaPipe Hands initialized")
    hands.close()
except Exception as e:
    print(f"✗ MediaPipe initialization failed: {e}")

# 测试摄像头
try:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✓ Camera opened successfully")
        ret, frame = cap.read()
        if ret:
            print(f"✓ Frame captured: {frame.shape}")
        cap.release()
    else:
        print("✗ Cannot open camera")
except Exception as e:
    print(f"✗ Camera test failed: {e}")

print("Diagnosis complete")