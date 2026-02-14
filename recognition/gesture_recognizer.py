#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手势识别器类 - 点击控制版本
负责识别各种手势类型，支持点击和滚轮控制
"""

from typing import Any
import math
import time


class GestureRecognizer:
    """手势识别器类 - 五指张开鼠标控制版本"""
    
    def __init__(self):
        # 手势识别阈值设置
        self.thresholds = {
            'pinch': 0.06,          # 精确触碰阈值
            'fist': 0.12,           # 握拳阈值
            'click_contact': 0.05,  # 点击接触阈值
            'finger_proximity': 0.04 # 手指靠近阈值
        }
        
        # 消抖和稳定性控制
        self.last_gesture = "无"
        self.stable_count = 0
        self.stability_required = 1  # 降低稳定性要求，提高响应性
        
        # 手势历史记录用于消抖
        self.gesture_history = []
        self.history_size = 8  # 历史记录长度
        
        # 手掌张开检测相关
        # 移除与"回到桌面"功能相关的变量
        # self.open_palm_detected = False
        # self.fist_transition_timer = 0
        # self.transition_timeout = 2.0  # 2秒超时
        
        # 缓存最近的手部关键点数据
        self.hand_landmarks_cache = None
        
        # 手腕移动检测相关
        self.last_wrist_position = (0.5, 0.5)
        self.wrist_movement_threshold = 0.02  # 手腕移动阈值
    
    def recognize_gesture(self, hand_landmarks: Any) -> str:
        """识别手势类型 - 手腕控制版本"""
        try:
            # 基础完整性检查
            if not hasattr(hand_landmarks, 'landmark') or len(hand_landmarks.landmark) < 21:
                return self._get_stable_result("无")
            
            # 缓存手部数据
            self.hand_landmarks_cache = hand_landmarks
            
            # 识别手势
            current_gesture = self._wrist_control_recognition(hand_landmarks)
            
            # 添加到历史记录
            self.gesture_history.append(current_gesture)
            if len(self.gesture_history) > self.history_size:
                self.gesture_history.pop(0)
            
            # 使用多数投票和稳定性检查
            stable_gesture = self._apply_debouncing(current_gesture)
            
            # 返回稳定结果
            return self._get_stable_result(stable_gesture)
            
        except Exception as e:
            print(f"手势识别出错: {e}")
            return self._get_stable_result("无")
    
    def _wrist_control_recognition(self, hand_landmarks: Any) -> str:
        """手腕控制手势识别核心逻辑"""
        try:
            # 获取关键点
            thumb_tip = hand_landmarks.landmark[4]    # 拇指尖
            thumb_ip = hand_landmarks.landmark[3]     # 拇指中间关节
            thumb_mcp = hand_landmarks.landmark[2]    # 拇指基部关节
            
            index_tip = hand_landmarks.landmark[8]    # 食指尖
            index_dip = hand_landmarks.landmark[7]    # 食指远端关节
            index_pip = hand_landmarks.landmark[6]    # 食指中间关节
            index_mcp = hand_landmarks.landmark[5]    # 食指基部关节
            
            middle_tip = hand_landmarks.landmark[12]  # 中指尖
            middle_dip = hand_landmarks.landmark[11]  # 中指远端关节
            middle_pip = hand_landmarks.landmark[10]  # 中指中间关节
            middle_mcp = hand_landmarks.landmark[9]   # 中指基部关节
            
            ring_tip = hand_landmarks.landmark[16]    # 无名指尖
            ring_dip = hand_landmarks.landmark[15]    # 无名指远端关节
            ring_pip = hand_landmarks.landmark[14]    # 无名指中间关节
            
            pinky_tip = hand_landmarks.landmark[20]   # 小指尖
            pinky_dip = hand_landmarks.landmark[19]   # 小指远端关节
            pinky_pip = hand_landmarks.landmark[18]   # 小指中间关节
            
            wrist = hand_landmarks.landmark[0]        # 手腕
            
            # 计算各种精确距离
            # 1. 拇指和食指指尖触碰（鼠标点击）
            thumb_index_tip_distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + 
                                               (thumb_tip.y - index_tip.y)**2)
            
            # 2. 拇指和中指指尖触碰（鼠标右键）
            thumb_middle_tip_distance = math.sqrt((thumb_tip.x - middle_tip.x)**2 + 
                                                (thumb_tip.y - middle_tip.y)**2)
            
            # 3. 拇指尖与食指DIP关节触碰（下滚轮）- 对应原来的4和7
            thumb_index_dip_distance = math.sqrt((thumb_tip.x - index_dip.x)**2 + 
                                               (thumb_tip.y - index_dip.y)**2)
            
            # 4. 拇指尖与食指PIP关节触碰（上滚轮）- 对应原来的4和6
            thumb_index_pip_distance = math.sqrt((thumb_tip.x - index_pip.x)**2 + 
                                               (thumb_tip.y - index_pip.y)**2)
            
            # 5. 食指和中指指尖距离（辅助检测）
            index_middle_tip_distance = math.sqrt((index_tip.x - middle_tip.x)**2 + 
                                                (index_tip.y - middle_tip.y)**2)
            
            # 检查握拳状态（最高优先级）
            bent_fingers = 0
            finger_tips = [8, 12, 16, 20]  # 食指、中指、无名指、小指
            
            for tip_id in finger_tips:
                tip = hand_landmarks.landmark[tip_id]
                distance = math.sqrt((tip.x - wrist.x)**2 + (tip.y - wrist.y)**2)
                if distance < self.thresholds['fist']:
                    bent_fingers += 1
            
            # 握拳检测（最高优先级）
            if bent_fingers >= 3:
                # 大部分手指弯曲 = 握拳（停止控制）
                return "握拳"
            
            # 手势判断（按优先级顺序）
            # 1. 点击相关手势（高优先级）
            if thumb_index_tip_distance < self.thresholds['click_contact']:
                # 拇指和食指指尖触碰 = 鼠标点击
                return "鼠标点击"
            
            elif thumb_middle_tip_distance < self.thresholds['click_contact']:
                # 拇指和中指指尖触碰 = 鼠标右键
                return "鼠标右键"
            
            # 2. 滚轮相关手势（中等优先级）
            elif thumb_index_dip_distance < self.thresholds['click_contact'] and bent_fingers < 2:
                # 拇指尖与食指DIP关节触碰 = 下滚轮
                return "下滚轮"
            
            elif thumb_index_pip_distance < self.thresholds['click_contact'] and bent_fingers < 2:
                # 拇指尖与食指PIP关节触碰 = 上滚轮
                return "上滚轮"
            
            # 3. 手腕移动检测（基础控制）
            current_wrist_pos = (wrist.x, wrist.y)
            wrist_movement = math.sqrt((current_wrist_pos[0] - self.last_wrist_position[0])**2 + 
                                     (current_wrist_pos[1] - self.last_wrist_position[1])**2)
            
            # 更新手腕位置
            self.last_wrist_position = current_wrist_pos
            
            # 如果手腕有明显移动，则触发鼠标移动
            if wrist_movement > self.wrist_movement_threshold:
                return "鼠标移动"
            
            # 4. 默认状态
            return "无"
                
        except Exception as e:
            print(f"手腕控制手势识别逻辑出错: {e}")
            return "无"
    
    def _is_finger_extended(self, hand_landmarks: Any, finger_tip_id: int, wrist) -> bool:
        """判断手指是否伸直"""
        try:
            finger_tip = hand_landmarks.landmark[finger_tip_id]
            # 手指尖应该明显高于手腕位置
            return finger_tip.y < (wrist.y - 0.1)
        except:
            return False
    
    def _is_thumb_extended(self, hand_landmarks: Any, wrist) -> bool:
        """判断拇指是否伸直（特殊处理）"""
        try:
            thumb_tip = hand_landmarks.landmark[4]
            thumb_mcp = hand_landmarks.landmark[2]
            # 拇指需要横向伸展，检查x坐标差异
            thumb_extended_horizontally = abs(thumb_tip.x - thumb_mcp.x) > 0.05
            # 同时拇指尖不能太低
            thumb_not_too_low = thumb_tip.y < (wrist.y + 0.05)
            return thumb_extended_horizontally and thumb_not_too_low
        except:
            return False
    
    def _apply_debouncing(self, current_gesture: str) -> str:
        """应用消抖算法"""
        if len(self.gesture_history) < self.history_size:
            return current_gesture
        
        # 统计历史手势频率
        gesture_counts = {}
        for gesture in self.gesture_history[-self.history_size:]:
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
        
        # 找出最常见的手势
        most_common_gesture = max(gesture_counts.items(), key=lambda x: x[1])[0]
        most_common_count = gesture_counts[most_common_gesture]
        
        # 对于点击类手势，降低判定门槛
        click_gestures = ["鼠标点击", "鼠标右键", "下滚轮", "上滚轮"]
        if current_gesture in click_gestures:
            # 点击手势只要有30%的比例就采用
            if gesture_counts.get(current_gesture, 0) / self.history_size >= 0.3:
                return current_gesture
        
        # 对于握拳手势（停止控制），给予最高优先级
        if current_gesture == "握拳":
            # 握拳手势只要有20%的比例就采用（因为它是停止控制的重要手势）
            if gesture_counts.get(current_gesture, 0) / self.history_size >= 0.2:
                return current_gesture
        
        # 对于其他手势，需要60%比例
        elif most_common_count / self.history_size >= 0.6:
            return most_common_gesture
        else:
            # 否则保持当前手势（防止频繁切换）
            return self.last_gesture if self.last_gesture != "无" else current_gesture
    
    def _get_stable_result(self, current_gesture: str) -> str:
        """获取稳定的手势识别结果"""
        # 稳定性处理
        if current_gesture == self.last_gesture:
            self.stable_count += 1
        else:
            self.stable_count = 1
            self.last_gesture = current_gesture
        
        # 只有达到稳定性要求才返回新结果
        if self.stable_count >= self.stability_required:
            return current_gesture
        else:
            # 如果是有效手势且至少有一帧记录，返回当前手势而不是"无"
            if current_gesture != "无" and self.stable_count >= 1:
                return current_gesture
            else:
                return self.last_gesture if self.stable_count > 1 else "无"
    
    def update_thresholds(self, pinch_threshold: float = None, 
                         fist_threshold: float = None, 
                         click_contact_threshold: float = None,
                         finger_proximity_threshold: float = None):
        """更新手势识别阈值"""
        if pinch_threshold is not None:
            self.thresholds['pinch'] = max(0.03, min(0.12, pinch_threshold))
        if fist_threshold is not None:
            self.thresholds['fist'] = max(0.08, min(0.2, fist_threshold))
        if click_contact_threshold is not None:
            self.thresholds['click_contact'] = max(0.03, min(0.08, click_contact_threshold))
        if finger_proximity_threshold is not None:
            self.thresholds['finger_proximity'] = max(0.02, min(0.08, finger_proximity_threshold))
    
    def get_thresholds(self):
        """获取当前阈值设置"""
        return self.thresholds.copy()
    
    def reset_stability(self):
        """重置稳定性计数器"""
        self.stable_count = 0
        self.last_gesture = "无"
        self.gesture_history.clear()
        self.last_wrist_position = (0.5, 0.5)
    
    def get_hand_center(self):
        """获取手部中心坐标（用于鼠标移动）- 现在返回点5（食指基部关节）坐标"""
        if self.hand_landmarks_cache:
            try:
                # 使用点5（食指基部关节）作为鼠标控制点
                index_mcp = self.hand_landmarks_cache.landmark[5]
                return index_mcp.x, index_mcp.y
            except:
                return 0.5, 0.5  # 默认中心位置
        return 0.5, 0.5
        
    def update_wrist_movement_threshold(self, threshold: float):
        """更新手腕移动阈值"""
        self.wrist_movement_threshold = max(0.01, min(0.1, threshold))