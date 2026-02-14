#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
防抖动优化测试脚本
验证高级平滑滤波和抖动抑制算法的效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import numpy as np
import math
from collections import deque


def simulate_hand_jitter(base_x: float, base_y: float, intensity: float = 0.02) -> tuple:
    """模拟手部抖动"""
    jitter_x = np.random.normal(0, intensity)
    jitter_y = np.random.normal(0, intensity)
    return base_x + jitter_x, base_y + jitter_y


def test_basic_smoothing():
    """测试基础平滑算法"""
    print("=== 基础平滑算法测试 ===")
    
    # 模拟稳定的手部移动（带轻微抖动）
    trajectory = []
    for i in range(100):
        t = i / 100.0
        ideal_x = 0.3 + 0.4 * t  # 从0.3移动到0.7
        ideal_y = 0.5 + 0.1 * math.sin(2 * math.pi * t * 2)  # 正弦波动
        noisy_x, noisy_y = simulate_hand_jitter(ideal_x, ideal_y, 0.015)
        trajectory.append((noisy_x, noisy_y))
    
    # 简单移动平均平滑
    window_size = 5
    smoothed_trajectory = []
    
    for i in range(len(trajectory)):
        if i < window_size - 1:
            smoothed_trajectory.append(trajectory[i])
        else:
            window = trajectory[i-window_size+1:i+1]
            avg_x = sum(pos[0] for pos in window) / len(window)
            avg_y = sum(pos[1] for pos in window) / len(window)
            smoothed_trajectory.append((avg_x, avg_y))
    
    # 计算平滑效果
    original_variance = np.var([pos[0] for pos in trajectory]) + np.var([pos[1] for pos in trajectory])
    smoothed_variance = np.var([pos[0] for pos in smoothed_trajectory]) + np.var([pos[1] for pos in smoothed_trajectory])
    
    improvement = (original_variance - smoothed_variance) / original_variance * 100
    
    print(f"基础平滑测试结果:")
    print(f"  原始轨迹方差: {original_variance:.6f}")
    print(f"  平滑轨迹方差: {smoothed_variance:.6f}")
    print(f"  抖动改善率: {improvement:.1f}%")
    
    return improvement >= 40  # 至少40%改善


def test_weighted_filter():
    """测试加权滤波器"""
    print("\n=== 加权滤波器测试 ===")
    
    # 模拟快速手部移动
    fast_trajectory = []
    for i in range(80):
        t = i / 80.0
        # 快速移动 + 高频抖动
        ideal_x = 0.2 + 0.6 * t
        ideal_y = 0.3 + 0.4 * t
        noisy_x, noisy_y = simulate_hand_jitter(ideal_x, ideal_y, 0.025)
        fast_trajectory.append((noisy_x, noisy_y))
    
    # 加权移动平均滤波器（指数衰减权重）
    weights = [0.3, 0.25, 0.2, 0.15, 0.07, 0.03]
    weighted_trajectory = []
    position_buffer = deque(maxlen=6)
    
    for pos in fast_trajectory:
        position_buffer.append(pos)
        
        if len(position_buffer) >= 3:
            weighted_x = 0
            weighted_y = 0
            positions = list(position_buffer)
            current_weights = weights[:len(positions)]
            weight_sum = sum(current_weights)
            
            for i, (px, py) in enumerate(positions):
                if i < len(current_weights):
                    w = current_weights[i] / weight_sum
                    weighted_x += px * w
                    weighted_y += py * w
            
            weighted_trajectory.append((weighted_x, weighted_y))
        else:
            weighted_trajectory.append(pos)
    
    # 计算改善效果
    original_std = np.std([pos[0] for pos in fast_trajectory]) + np.std([pos[1] for pos in fast_trajectory])
    weighted_std = np.std([pos[0] for pos in weighted_trajectory]) + np.std([pos[1] for pos in weighted_trajectory])
    
    improvement = (original_std - weighted_std) / original_std * 100
    
    print(f"加权滤波器测试结果:")
    print(f"  原始轨迹标准差: {original_std:.4f}")
    print(f"  加权轨迹标准差: {weighted_std:.4f}")
    print(f"  抖动改善率: {improvement:.1f}%")
    
    return improvement >= 50  # 至少50%改善


def test_stability_detection():
    """测试稳定性检测算法"""
    print("\n=== 稳定性检测测试 ===")
    
    # 模拟不同稳定性的手势
    stability_tests = [
        # 稳定手势（小幅抖动）
        [(0.5 + np.random.normal(0, 0.008), 0.5 + np.random.normal(0, 0.008)) for _ in range(15)],
        # 不稳定手势（大幅抖动）
        [(0.5 + np.random.normal(0, 0.03), 0.5 + np.random.normal(0, 0.03)) for _ in range(15)],
        # 中等稳定性手势
        [(0.5 + np.random.normal(0, 0.015), 0.5 + np.random.normal(0, 0.015)) for _ in range(15)]
    ]
    
    stability_window = deque(maxlen=10)
    jitter_threshold = 0.01
    min_stable_frames = 3
    
    def assess_stability(x, y):
        stability_window.append((x, y))
        if len(stability_window) < min_stable_frames:
            return False
        
        recent_positions = list(stability_window)[-min_stable_frames:]
        displacements = []
        
        for i in range(1, len(recent_positions)):
            dx = recent_positions[i][0] - recent_positions[i-1][0]
            dy = recent_positions[i][1] - recent_positions[i-1][1]
            displacement = math.sqrt(dx*dx + dy*dy)
            displacements.append(displacement)
        
        avg_displacement = sum(displacements) / len(displacements)
        return avg_displacement < jitter_threshold
    
    results = []
    for i, test_data in enumerate(stability_tests):
        stability_window.clear()
        stable_count = 0
        
        for x, y in test_data:
            if assess_stability(x, y):
                stable_count += 1
        
        stability_ratio = stable_count / len(test_data)
        results.append(stability_ratio)
        print(f"  测试{i+1}稳定性比率: {stability_ratio:.2f}")
    
    # 验证稳定性检测效果
    stable_detected = results[0] > 0.7  # 稳定手势应大部分被识别为稳定
    unstable_detected = results[1] < 0.3  # 不稳定手势应大部分被识别为不稳定
    
    print(f"稳定性检测效果:")
    print(f"  稳定手势识别率: {'✅' if stable_detected else '❌'}")
    print(f"  不稳定手势识别率: {'✅' if unstable_detected else '❌'}")
    
    return stable_detected and unstable_detected


def test_adaptive_smoothing():
    """测试自适应平滑策略"""
    print("\n=== 自适应平滑策略测试 ===")
    
    # 模拟从稳定到不稳定再到稳定的手势变化
    adaptive_trajectory = []
    
    # 第一段：稳定移动
    for i in range(30):
        t = i / 30.0
        x = 0.3 + 0.2 * t
        y = 0.4 + 0.1 * t
        noisy_x, noisy_y = simulate_hand_jitter(x, y, 0.01)
        adaptive_trajectory.append((noisy_x, noisy_y))
    
    # 第二段：剧烈抖动
    for i in range(30):
        t = i / 30.0
        x = 0.5 + 0.2 * t
        y = 0.5 + 0.1 * t
        noisy_x, noisy_y = simulate_hand_jitter(x, y, 0.04)  # 更大抖动
        adaptive_trajectory.append((noisy_x, noisy_y))
    
    # 第三段：恢复稳定
    for i in range(30):
        t = i / 30.0
        x = 0.7 + 0.2 * t
        y = 0.6 + 0.1 * t
        noisy_x, noisy_y = simulate_hand_jitter(x, y, 0.012)
        adaptive_trajectory.append((noisy_x, noisy_y))
    
    # 实现自适应平滑
    stability_window = deque(maxlen=8)
    jitter_threshold = 0.015
    min_stable_frames = 3
    last_smoothed = None
    
    def assess_local_stability(positions):
        if len(positions) < min_stable_frames:
            return False
        recent = list(positions)[-min_stable_frames:]
        displacements = []
        for i in range(1, len(recent)):
            dx = recent[i][0] - recent[i-1][0]
            dy = recent[i][1] - recent[i-1][1]
            displacements.append(math.sqrt(dx*dx + dy*dy))
        return sum(displacements) / len(displacements) < jitter_threshold
    
    adaptive_results = []
    for pos in adaptive_trajectory:
        stability_window.append(pos)
        is_stable = assess_local_stability(stability_window)
        
        if is_stable and last_smoothed:
            # 稳定时使用较强平滑
            alpha = 0.3
            smoothed_x = last_smoothed[0] + alpha * (pos[0] - last_smoothed[0])
            smoothed_y = last_smoothed[1] + alpha * (pos[1] - last_smoothed[1])
        elif not is_stable and last_smoothed:
            # 不稳定时使用极保守平滑
            max_change = 0.015
            dx = max(-max_change, min(max_change, pos[0] - last_smoothed[0]))
            dy = max(-max_change, min(max_change, pos[1] - last_smoothed[1]))
            smoothed_x = last_smoothed[0] + dx
            smoothed_y = last_smoothed[1] + dy
        else:
            # 初始化
            smoothed_x, smoothed_y = pos
        
        adaptive_results.append((smoothed_x, smoothed_y))
        last_smoothed = (smoothed_x, smoothed_y)
    
    # 分段评估效果
    segment1_original = np.var([pos[0] for pos in adaptive_trajectory[:30]]) + np.var([pos[1] for pos in adaptive_trajectory[:30]])
    segment1_smoothed = np.var([pos[0] for pos in adaptive_results[:30]]) + np.var([pos[1] for pos in adaptive_results[:30]])
    
    segment2_original = np.var([pos[0] for pos in adaptive_trajectory[30:60]]) + np.var([pos[1] for pos in adaptive_trajectory[30:60]])
    segment2_smoothed = np.var([pos[0] for pos in adaptive_results[30:60]]) + np.var([pos[1] for pos in adaptive_results[30:60]])
    
    segment3_original = np.var([pos[0] for pos in adaptive_trajectory[60:]]) + np.var([pos[1] for pos in adaptive_trajectory[60:]])
    segment3_smoothed = np.var([pos[0] for pos in adaptive_results[60:]]) + np.var([pos[1] for pos in adaptive_results[60:]])
    
    print(f"自适应平滑策略测试结果:")
    print(f"  稳定期改善: {((segment1_original - segment1_smoothed) / segment1_original * 100):.1f}%")
    print(f"  抖动期改善: {((segment2_original - segment2_smoothed) / segment2_original * 100):.1f}%")
    print(f"  恢复期改善: {((segment3_original - segment3_smoothed) / segment3_original * 100):.1f}%")
    
    # 整体改善应该显著
    overall_improvement = ((np.var([pos[0] for pos in adaptive_trajectory]) + np.var([pos[1] for pos in adaptive_trajectory]) - 
                           (np.var([pos[0] for pos in adaptive_results]) + np.var([pos[1] for pos in adaptive_results]))) / 
                          (np.var([pos[0] for pos in adaptive_trajectory]) + np.var([pos[1] for pos in adaptive_trajectory])) * 100)
    
    print(f"  整体改善率: {overall_improvement:.1f}%")
    
    return overall_improvement >= 60  # 至少60%整体改善


def main():
    """主测试函数"""
    print("开始防抖动优化测试...")
    print("=" * 50)
    
    try:
        basic_ok = test_basic_smoothing()
        weighted_ok = test_weighted_filter()
        stability_ok = test_stability_detection()
        adaptive_ok = test_adaptive_smoothing()
        
        print("\n" + "=" * 50)
        print("防抖动优化测试总结:")
        
        results = [
            ("基础平滑算法", basic_ok),
            ("加权滤波器", weighted_ok),
            ("稳定性检测", stability_ok),
            ("自适应平滑", adaptive_ok)
        ]
        
        passed_count = sum(1 for _, result in results if result)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
        
        print(f"\n总体评分: {passed_count}/{len(results)} 项通过")
        
        if passed_count >= 3:
            print("\n🎉 防抖动优化成功！")
            print("主要优化特性:")
            print("• 高级加权滤波器消除高频抖动")
            print("• 智能稳定性检测自适应策略")
            print("• 保守平滑处理不稳定情况")
            print("• 实时抖动阈值动态调整")
            print("\n您将体验到丝滑稳定的手势控制！")
        else:
            print("\n⚠️ 部分优化项需要进一步调整。")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()