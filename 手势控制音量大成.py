import cv2
import mediapipe as mp
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# 灵敏度调节除数，用户可根据实际需求修改此值来调整灵敏度，数值越大灵敏度越低
sensitivity_divisor = 1.5

# 获取音量控制接口
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# 获取音量范围
volume_range = volume.GetVolumeRange()
min_volume = volume_range[0]
max_volume = volume_range[1]


# 计算两个手部位置中心之间的距离
def hand_distance(hand1, hand2):
    x1, y1 = hand1
    x2, y2 = hand2
    # 使用绝对值确保距离为正数，避免出现负数距离的情况
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# 打开摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头，请检查摄像头是否连接正常或者是否被其他程序占用。")
    exit(1)

with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # 水平翻转图像以获得更自然的视觉效果（类似镜像）
        frame = cv2.flip(frame, 1)
        # 将BGR图像转换为RGB，MediaPipe要求的输入格式
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(image_rgb)
        # 增加对results.multi_hand_landmarks是否为None的判断，避免出现NoneType不可迭代的问题
        if results and results.multi_hand_landmarks:
            hands_centers = []
            for hand_landmarks in results.multi_hand_landmarks:
                # 采用多个关键点加权平均的方式来确定手部中心位置，可使计算更精准，这里权重可根据实际情况调整
                hand_center_x = 0
                hand_center_y = 0
                weights = [0.2, 0.2, 0.2, 0.2, 0.2]
                landmark_indices = [mp_hands.HandLandmark.WRIST, mp_hands.HandLandmark.THUMB_CMC,
                                    mp_hands.HandLandmark.INDEX_FINGER_MCP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
                                    mp_hands.HandLandmark.RING_FINGER_MCP]
                for index, landmark_index in enumerate(landmark_indices):
                    landmark = hand_landmarks.landmark[landmark_index]
                    hand_center_x += landmark.x * frame.shape[1] * weights[index]
                    hand_center_y += landmark.y * frame.shape[0] * weights[index]
                hands_centers.append((int(hand_center_x), int(hand_center_y)))

            if len(hands_centers) == 2:
                dist = hand_distance(hands_centers[0], hands_centers[1])
                # 将距离映射到音量范围，根据距离变化调整音量，距离越大音量越大，距离为0时音量为最小音量
                normalized_dist = np.clip(dist / (frame.shape[1] / sensitivity_divisor), 0, 1)
                volume_value = min_volume + (max_volume - min_volume) * normalized_dist
                volume.SetMasterVolumeLevel(volume_value, None)
                # 在图像上绘制当前音量值，作为可视化反馈元素，方便用户了解音量状态
                volume_text = f"Volume: {int(volume_value)}"
                cv2.putText(frame, volume_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                # 若未检测到两只手，显示提示信息表示当前无法调节音量
                cv2.putText(frame, "Volume: Unable to adjust (Need 2 hands)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            # 若未检测到手部或者results.multi_hand_landmarks为None，显示提示信息表示未检测到手部
            cv2.putText(frame, "Volume: No hands detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 在图像上绘制手部地标和连接（需要确保results.multi_hand_landmarks不为None才能进行绘制）
        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
