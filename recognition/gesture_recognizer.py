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
    def __init__(self):
        self.thresholds = {
            'pinch': 0.06,
            'fist': 0.15,
            'click_contact': 0.05,
            'finger_proximity': 0.1,
            'wheel_up_threshold': 0.04,
            'wheel_down_threshold': 0.04
        }
        self.last_gesture = "无"
        self.stable_count = 0
        self.stability_required = 1
        self.gesture_history = []
        self.history_size = 8
        self.hand_landmarks_cache = None
        self.last_wrist_position = (0.5, 0.5)
        self.wrist_movement_threshold = 0.01 # contorl move scale
    
    def recognize_gesture(self, hand_landmarks: Any) -> str:
        try:
            if not hasattr(hand_landmarks, 'landmark') or len(hand_landmarks.landmark) < 21:
                return self._get_stable_result("无")
            self.hand_landmarks_cache = hand_landmarks
            current_gesture = self._wrist_control_recognition(hand_landmarks)
            self.gesture_history.append(current_gesture)
            if len(self.gesture_history) > self.history_size:
                self.gesture_history.pop(0)
            stable_gesture = self._apply_debouncing(current_gesture)
            return self._get_stable_result(stable_gesture)
        except Exception as e:
            print(f"手势识别出错: {e}")
            return self._get_stable_result("无")
    
    def _wrist_control_recognition(self, hand_landmarks: Any) -> str:
        try:
            thumb_tip = hand_landmarks.landmark[4]
            thumb_ip = hand_landmarks.landmark[3]
            thumb_mcp = hand_landmarks.landmark[2]
            
            index_tip = hand_landmarks.landmark[8]
            index_dip = hand_landmarks.landmark[7]
            index_pip = hand_landmarks.landmark[6]
            index_mcp = hand_landmarks.landmark[5]
            
            middle_tip = hand_landmarks.landmark[12]
            middle_dip = hand_landmarks.landmark[11]
            middle_pip = hand_landmarks.landmark[10]
            middle_mcp = hand_landmarks.landmark[9]
            
            ring_tip = hand_landmarks.landmark[16]
            ring_dip = hand_landmarks.landmark[15]
            ring_pip = hand_landmarks.landmark[14]
            
            pinky_tip = hand_landmarks.landmark[20]
            pinky_dip = hand_landmarks.landmark[19]
            pinky_pip = hand_landmarks.landmark[18]
            
            wrist = hand_landmarks.landmark[0]
            

            thumb_index_tip_distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + 
                                               (thumb_tip.y - index_tip.y)**2)
            
            thumb_middle_tip_distance = math.sqrt((thumb_tip.x - middle_tip.x)**2 + 
                                                (thumb_tip.y - middle_tip.y)**2)
            
            thumb_index_mcp_distance = math.sqrt((thumb_tip.x - index_mcp.x)**2 + 
                                               (thumb_tip.y - index_mcp.y)**2)
            
            thumb_index_pip_distance = math.sqrt((thumb_tip.x - index_pip.x)**2 + 
                                               (thumb_tip.y - index_pip.y)**2)
            
            bent_fingers = 0
            finger_tips = [8, 12, 16, 20]
            
            for tip_id in finger_tips:
                tip = hand_landmarks.landmark[tip_id]
                distance = math.sqrt((tip.x - wrist.x)**2 + (tip.y - wrist.y)**2)
                if distance < self.thresholds['fist']:
                    bent_fingers += 1
            if bent_fingers >= 3:
                return "握拳"
            
            if thumb_index_tip_distance < self.thresholds['click_contact']:
                return "鼠标点击"
            
            elif thumb_middle_tip_distance < self.thresholds['click_contact']:
                return "鼠标右键"
            
            elif thumb_index_pip_distance < self.thresholds['wheel_down_threshold'] and bent_fingers < 2:
                if thumb_index_mcp_distance >= self.thresholds['wheel_up_threshold']:
                    return "下滚轮"
                else:
                    if thumb_index_pip_distance <= thumb_index_mcp_distance:
                        return "下滚轮"
                    else:
                        return "上滚轮"
            
            elif thumb_index_mcp_distance < self.thresholds['wheel_up_threshold'] and bent_fingers < 2:
                if thumb_index_pip_distance >= self.thresholds['wheel_down_threshold']:
                    return "上滚轮"
                else:
                    if thumb_index_mcp_distance <= thumb_index_pip_distance:
                        return "上滚轮"
                    else:
                        return "下滚轮"
            current_wrist_pos = (wrist.x, wrist.y)
            wrist_movement = math.sqrt((current_wrist_pos[0] - self.last_wrist_position[0])**2 + 
                                     (current_wrist_pos[1] - self.last_wrist_position[1])**2)
            self.last_wrist_position = current_wrist_pos
            
            if wrist_movement > self.wrist_movement_threshold:
                return "鼠标移动"
            return "无"
                
        except Exception as e:
            print(f"手腕控制手势识别逻辑出错: {e}")
            return "无"
    
    def _is_finger_extended(self, hand_landmarks: Any, finger_tip_id: int, wrist) -> bool:
        try:
            finger_tip = hand_landmarks.landmark[finger_tip_id]
            return finger_tip.y < (wrist.y - 0.1)
        except:
            return False
    
    def _is_thumb_extended(self, hand_landmarks: Any, wrist) -> bool:
        try:
            thumb_tip = hand_landmarks.landmark[4]
            thumb_mcp = hand_landmarks.landmark[2]
            thumb_extended_horizontally = abs(thumb_tip.x - thumb_mcp.x) > 0.05
            thumb_not_too_low = thumb_tip.y < (wrist.y + 0.05)
            return thumb_extended_horizontally and thumb_not_too_low
        except:
            return False
    
    def _apply_debouncing(self, current_gesture: str) -> str:
        if len(self.gesture_history) < self.history_size:
            return current_gesture
        gesture_counts = {}
        for gesture in self.gesture_history[-self.history_size:]:
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
        most_common_gesture = max(gesture_counts.items(), key=lambda x: x[1])[0]
        most_common_count = gesture_counts[most_common_gesture]
        click_gestures = ["鼠标点击", "鼠标右键", "下滚轮", "上滚轮"]
        if current_gesture in click_gestures:
            if gesture_counts.get(current_gesture, 0) / self.history_size >= 0.3:
                return current_gesture
        if current_gesture == "握拳":
            if gesture_counts.get(current_gesture, 0) / self.history_size >= 0.2:
                return current_gesture
        elif most_common_count / self.history_size >= 0.6:
            return most_common_gesture
        else:
            return self.last_gesture if self.last_gesture != "无" else current_gesture
    
    def _get_stable_result(self, current_gesture: str) -> str:
        if current_gesture == self.last_gesture:
            self.stable_count += 1
        else:
            self.stable_count = 1
            self.last_gesture = current_gesture
        if self.stable_count >= self.stability_required:
            return current_gesture
        else:
            if current_gesture != "无" and self.stable_count >= 1:
                return current_gesture
            else:
                return self.last_gesture if self.stable_count > 1 else "无"
    
    def update_thresholds(self, pinch_threshold: float = None, 
                         fist_threshold: float = None, 
                         click_contact_threshold: float = None,
                         finger_proximity_threshold: float = None,
                         wheel_up_threshold: float = None,
                         wheel_down_threshold: float = None):
        if pinch_threshold is not None:
            self.thresholds['pinch'] = max(0.03, min(0.12, pinch_threshold))
        if fist_threshold is not None:
            self.thresholds['fist'] = max(0.08, min(0.2, fist_threshold))
        if click_contact_threshold is not None:
            self.thresholds['click_contact'] = max(0.03, min(0.12, click_contact_threshold))
        if finger_proximity_threshold is not None:
            self.thresholds['finger_proximity'] = max(0.02, min(0.08, finger_proximity_threshold))
        if wheel_up_threshold is not None:
            self.thresholds['wheel_up_threshold'] = max(0.03, min(0.15, wheel_up_threshold))
        if wheel_down_threshold is not None:
            self.thresholds['wheel_down_threshold'] = max(0.03, min(0.15, wheel_down_threshold))
    
    def get_thresholds(self):
        return self.thresholds.copy()
    
    def reset_stability(self):
        self.stable_count = 0
        self.last_gesture = "无"
        self.gesture_history.clear()
        self.last_wrist_position = (0.5, 0.5)
    
    def get_hand_center(self):
        if self.hand_landmarks_cache:
            try:
                middle_mcp = self.hand_landmarks_cache.landmark[9]
                if 0 <= middle_mcp.x <= 1 and 0 <= middle_mcp.y <= 1:
                    # print(f"[DEBUG] 点9坐标: ({middle_mcp.x:.3f}, {middle_mcp.y:.3f})")
                    return middle_mcp.x, middle_mcp.y
                else:
                    print(f"[WARNING] 点9坐标超出有效范围: ({middle_mcp.x}, {middle_mcp.y})")
                    return 0.5, 0.5
            except Exception as e:
                print(f"[ERROR] 获取点9坐标失败: {e}")
                return 0.5, 0.5
        return 0.5, 0.5
        
    def update_wrist_movement_threshold(self, threshold: float):
        self.wrist_movement_threshold = max(0.01, min(0.1, threshold))