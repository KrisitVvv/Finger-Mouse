import mediapipe as mp
import cv2

print("MediaPipe版本:", mp.__version__)
print("是否有solutions:", hasattr(mp, 'solutions'))
print("是否有tasks:", hasattr(mp, 'tasks'))

if hasattr(mp, 'solutions'):
    print("尝试使用旧版API...")
    try:
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        print("旧版API初始化成功!")
    except Exception as e:
        print(f"旧版API初始化失败: {e}")

if hasattr(mp, 'tasks'):
    print("尝试使用新版API...")
    try:
        from mediapipe.tasks import vision
        print("新版API可用")
    except Exception as e:
        print(f"新版API初始化失败: {e}")

print("测试完成")