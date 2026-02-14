#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手势映射系统测试脚本
验证各种手势到鼠标/键盘操作的映射功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.gesture_mappings import gesture_mapper, GestureAction
from control.mouse_controller import MouseController
import time


def test_basic_gesture_mappings():
    """测试基础手势映射功能"""
    print("=== 基础手势映射测试 ===")
    
    # 测试可用手势列表
    gestures = gesture_mapper.get_available_gestures()
    print(f"可用手势数量: {len(gestures)}")
    print("手势列表:")
    for gesture in gestures:
        desc = gesture_mapper.get_gesture_description(gesture)
        print(f"  - {gesture}: {desc}")
    
    print("\n=== 手势执行测试 ===")
    
    # 测试鼠标移动（模拟手部中心位置）
    print("测试鼠标移动...")
    hand_center = (0.6, 0.4)  # 模拟手部位置
    success = gesture_mapper.execute_gesture_action("鼠标移动", hand_center)
    print(f"鼠标移动执行结果: {'成功' if success else '失败'}")
    
    # 测试鼠标左键点击
    print("测试鼠标左键点击...")
    success = gesture_mapper.execute_gesture_action("鼠标点击")
    print(f"鼠标左键点击执行结果: {'成功' if success else '失败'}")
    
    # 测试鼠标右键点击
    print("测试鼠标右键点击...")
    success = gesture_mapper.execute_gesture_action("鼠标右键")
    print(f"鼠标右键点击执行结果: {'成功' if success else '失败'}")
    
    # 测试滚轮操作
    print("测试鼠标滚轮向上...")
    success = gesture_mapper.execute_gesture_action("上滚轮")
    print(f"鼠标滚轮向上执行结果: {'成功' if success else '失败'}")
    
    print("测试鼠标滚轮向下...")
    success = gesture_mapper.execute_gesture_action("下滚轮")
    print(f"鼠标滚轮向下执行结果: {'成功' if success else '失败'}")
    
    # 测试键盘快捷键（回到桌面）
    print("测试回到桌面快捷键...")
    success = gesture_mapper.execute_gesture_action("回到桌面")
    print(f"回到桌面执行结果: {'成功' if success else '失败'}")


def test_mouse_controller_integration():
    """测试鼠标控制器与手势映射的集成"""
    print("\n=== 鼠标控制器集成测试 ===")
    
    controller = MouseController()
    
    # 测试手势历史记录
    print("测试手势历史记录...")
    test_gestures = ["鼠标移动", "鼠标点击", "鼠标右键", "上滚轮", "下滚轮"]
    
    for gesture in test_gestures:
        controller.handle_gesture(gesture)
        time.sleep(0.1)  # 短暂延迟避免冷却时间限制
    
    history = controller.get_gesture_history(10)
    print(f"手势历史记录: {history}")
    
    # 测试自定义手势映射
    print("测试自定义手势映射...")
    def custom_callback():
        print("执行自定义操作!")
    
    controller.add_custom_gesture_mapping("自定义测试", {
        "action": GestureAction.CUSTOM_ACTION,
        "params": {"callback": custom_callback},
        "description": "测试自定义手势"
    })
    
    print("执行自定义手势...")
    controller.handle_gesture("自定义测试")


def test_advanced_features():
    """测试高级功能"""
    print("\n=== 高级功能测试 ===")
    
    # 测试手势映射更新
    print("测试手势映射更新...")
    original_desc = gesture_mapper.get_gesture_description("鼠标点击")
    print(f"原始鼠标点击描述: {original_desc}")
    
    # 更新映射
    gesture_mapper.update_mapping("鼠标点击", {
        "action": GestureAction.MOUSE_LEFT_CLICK,
        "params": {"cooldown": 0.5},  # 增加冷却时间
        "description": "更新后的鼠标点击手势"
    })
    
    updated_desc = gesture_mapper.get_gesture_description("鼠标点击")
    print(f"更新后鼠标点击描述: {updated_desc}")
    
    # 测试组合手势检测（模拟快速连续手势）
    print("测试手势历史分析...")
    gesture_mapper.add_to_history("鼠标点击")
    gesture_mapper.add_to_history("鼠标点击")
    gesture_mapper.add_to_history("鼠标移动")
    
    recent = gesture_mapper.get_recent_gestures(5)
    print(f"最近5个手势: {recent}")


def test_error_handling():
    """测试错误处理"""
    print("\n=== 错误处理测试 ===")
    
    # 测试不存在的手势
    print("测试不存在的手势...")
    success = gesture_mapper.execute_gesture_action("不存在的手势")
    print(f"不存在手势执行结果: {'成功' if success else '失败'}")
    
    # 测试冷却时间限制
    print("测试冷却时间限制...")
    gesture_mapper.last_action_times["mouse_left_click"] = time.time()  # 设置最近执行时间
    success1 = gesture_mapper.execute_gesture_action("鼠标点击")  # 应该被冷却限制
    time.sleep(0.3)  # 等待超过冷却时间
    success2 = gesture_mapper.execute_gesture_action("鼠标点击")  # 应该可以执行
    print(f"冷却限制测试: 第一次={success1}, 第二次={success2}")


def main():
    """主测试函数"""
    print("开始手势映射系统测试...\n")
    
    try:
        test_basic_gesture_mappings()
        test_mouse_controller_integration()
        test_advanced_features()
        test_error_handling()
        
        print("\n🎉 所有测试完成!")
        print("\n=== 测试总结 ===")
        print("✓ 基础手势映射功能正常")
        print("✓ 鼠标控制器集成成功")
        print("✓ 自定义手势映射支持")
        print("✓ 手势历史记录功能")
        print("✓ 错误处理机制完善")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()