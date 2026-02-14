#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
鼠标控制功能诊断脚本
用于排查鼠标点击和移动无响应的问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from control.mouse_controller import MouseController
from pynput.mouse import Button
import time


def test_mouse_basic_functions():
    """测试鼠标基本功能"""
    print("=== 鼠标基本功能测试 ===")
    
    mouse = MouseController()
    
    # 测试1: 检查鼠标控制器初始化
    print("1. 鼠标控制器初始化检查...")
    print(f"   鼠标控制器实例: {mouse}")
    print(f"   鼠标位置: {mouse.get_current_position()}")
    print(f"   屏幕尺寸: {mouse.screen_width} x {mouse.screen_height}")
    
    # 测试2: 直接鼠标操作测试
    print("\n2. 直接鼠标操作测试...")
    try:
        # 获取当前位置
        original_pos = mouse.get_current_position()
        print(f"   原始位置: {original_pos}")
        
        # 移动鼠标
        mouse.move_mouse(0.1, 0.1)  # 移动到屏幕10%位置
        time.sleep(0.5)
        new_pos = mouse.get_current_position()
        print(f"   移动后位置: {new_pos}")
        
        # 点击测试
        print("   执行左键点击...")
        mouse.mouse.click(Button.left, 1)
        time.sleep(0.5)
        
        print("   执行右键点击...")
        mouse.mouse.click(Button.right, 1)
        time.sleep(0.5)
        
        # 滚轮测试
        print("   执行滚轮滚动...")
        mouse.scroll_mouse(3)
        time.sleep(0.5)
        
        # 恢复原位置
        mouse.mouse.position = original_pos
        print(f"   已恢复到原始位置: {original_pos}")
        
        print("✅ 直接鼠标操作测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 直接鼠标操作测试失败: {e}")
        return False


def test_gesture_handling():
    """测试手势处理功能"""
    print("\n=== 手势处理功能测试 ===")
    
    mouse = MouseController()
    
    # 测试3: 手势处理方法检查
    print("3. 手势处理方法检查...")
    print(f"   handle_gesture 方法存在: {hasattr(mouse, 'handle_gesture')}")
    print(f"   _handle_mouse_click 方法存在: {hasattr(mouse, '_handle_mouse_click')}")
    print(f"   _handle_mouse_movement 方法存在: {hasattr(mouse, '_handle_mouse_movement')}")
    
    # 测试4: 手势映射系统检查
    print("\n4. 手势映射系统检查...")
    try:
        from config.gesture_mappings import gesture_mapper
        print(f"   手势映射器实例: {gesture_mapper}")
        print(f"   可用手势数量: {len(gesture_mapper.get_available_gestures())}")
        print("   可用手势列表:")
        for gesture in gesture_mapper.get_available_gestures():
            desc = gesture_mapper.get_gesture_description(gesture)
            print(f"     - {gesture}: {desc}")
    except Exception as e:
        print(f"   手势映射系统加载失败: {e}")
    
    # 测试5: 手势处理测试
    print("\n5. 手势处理测试...")
    try:
        # 测试鼠标点击手势
        print("   测试鼠标点击手势...")
        mouse.handle_gesture("鼠标点击")
        time.sleep(1)
        
        # 测试鼠标移动手势（需要手部中心坐标）
        print("   测试鼠标移动手势...")
        mouse.handle_gesture("鼠标移动", (0.5, 0.5))  # 中心位置
        time.sleep(1)
        
        # 测试右键手势
        print("   测试鼠标右键手势...")
        mouse.handle_gesture("鼠标右键")
        time.sleep(1)
        
        print("✅ 手势处理测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 手势处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_recognizer():
    """测试与手势识别器的集成"""
    print("\n=== 与手势识别器集成测试 ===")
    
    try:
        from recognition.gesture_recognizer import GestureRecognizer
        
        # 创建识别器和控制器
        recognizer = GestureRecognizer()
        mouse = MouseController()
        
        print("6. 集成测试准备...")
        print(f"   手势识别器: {recognizer}")
        print(f"   鼠标控制器: {mouse}")
        
        # 测试手部中心获取
        print("\n7. 手部中心坐标测试...")
        hand_center = recognizer.get_hand_center()
        print(f"   默认手部中心: {hand_center}")
        
        # 测试完整的处理链路
        print("\n8. 完整处理链路测试...")
        test_gestures = ["鼠标点击", "鼠标移动", "鼠标右键", "下滚轮", "上滚轮"]
        
        for gesture in test_gestures:
            print(f"   测试手势: {gesture}")
            try:
                if gesture == "鼠标移动":
                    mouse.handle_gesture(gesture, hand_center)
                else:
                    mouse.handle_gesture(gesture)
                print(f"     ✓ {gesture} 处理成功")
            except Exception as e:
                print(f"     ✗ {gesture} 处理失败: {e}")
            time.sleep(0.5)
        
        print("✅ 集成测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主诊断函数"""
    print("开始鼠标控制功能诊断...")
    print("=" * 50)
    
    results = []
    
    # 执行各项测试
    results.append(test_mouse_basic_functions())
    results.append(test_gesture_handling())
    results.append(test_integration_with_recognizer())
    
    # 输出总结
    print("\n" + "=" * 50)
    print("诊断结果总结:")
    print(f"通过测试: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 所有测试通过！鼠标控制功能正常")
        print("\n建议检查:")
        print("1. 确认摄像头能够正确识别手势")
        print("2. 检查手势识别结果是否正确传递")
        print("3. 确认鼠标控制开关已启用")
        print("4. 查看是否有权限问题阻止鼠标控制")
    else:
        print("❌ 部分测试失败，请根据上面的错误信息进行修复")
    
    return all(results)


if __name__ == "__main__":
    main()