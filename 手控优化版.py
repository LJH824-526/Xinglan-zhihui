import cv2
import mediapipe as mp
import numpy as np
import win32api
import win32con
import time

# 导入 OpenCV 库，用于图像和视频处理
import cv2
# 导入 MediaPipe 库，用于手部关键点检测等
import mediapipe as mp
# 导入 NumPy 库，用于数值计算，如数组操作等
import numpy as np
# 导入 win32api 和 win32con 库，用于模拟鼠标操作
import win32api
import win32con
# 导入 time 库，用于在代码中添加时间延迟
import time

# 从 MediaPipe 中导入绘图工具，用于在图像上绘制手部地标和连接
mp_drawing = mp.solutions.drawing_utils
# 从 MediaPipe 中导入手部检测模块
mp_hands = mp.solutions.hands

# 打开默认摄像头，0 通常表示系统默认的视频捕获设备
cap = cv2.VideoCapture(0)

# 初始化变量，用于记录上一帧右手食指的位置
prev_right_index_pos = None
# 设置提高右手移动灵敏度的缩放因子为 2，这将使右手食指控制鼠标移动更加灵敏
movement_scaling_factor = 2

# 使用 MediaPipe 的手部检测模块创建一个手部检测对象
# static_image_mode=False 表示用于处理视频流而不是静态图像
# max_num_hands=2 表示最多检测两只手
# min_detection_confidence=0.5 和 min_tracking_confidence=0.5 表示检测和跟踪的置信度阈值
with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while True:
        # 从摄像头读取一帧图像
        ret, frame = cap.read()
        # 如果读取失败，即没有成功获取到帧，退出循环
        if not ret:
            break
        # 水平翻转图像，以获得更自然的视觉效果，类似镜像
        frame = cv2.flip(frame, 1)
        # 将图像的颜色格式从 BGR（OpenCV 默认）转换为 RGB，这是 MediaPipe 手部检测要求的输入格式
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 使用创建的手部检测对象对转换后的图像进行手部关键点检测
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            # 如果检测到了手部关键点，则遍历每只手的地标信息
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 获取当前手的左右性，即判断是左手还是右手
                handedness = results.multi_handedness[hand_idx].classification[0].label

                if handedness == "Right":
                    # 找到右手食指尖在图像中的位置
                    # hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP] 获取右手食指尖的关键点信息
                    #.x 和.y 分别是该关键点在归一化坐标中的 x 和 y 坐标值
                    # 乘以 frame.shape[1] 和 frame.shape[0] 将归一化坐标转换为图像的实际像素坐标
                    index_finger_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame.shape[1]
                    index_finger_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame.shape[0]
                    # 将像素坐标转换为整数，并存储为右手食指的位置
                    right_index_pos = (int(index_finger_tip_x), int(index_finger_tip_y))

                    if prev_right_index_pos:
                        # 计算当前帧与上一帧右手食指位置的位移
                        # prev_right_index_pos[0] - right_index_pos[0] 计算水平方向的位移
                        # prev_right_index_pos[1] - right_index_pos[1] 计算垂直方向的位移
                        # 乘以 movement_scaling_factor 提高右手移动的灵敏度为原来的 2 倍
                        dx = (prev_right_index_pos[0] - right_index_pos[0]) * movement_scaling_factor
                        dy = (right_index_pos[1] - prev_right_index_pos[1]) * movement_scaling_factor
                        # 增加稳定性，限制最大移动距离
                        max_move = 100
                        # np.clip 函数将位移限制在 -max_move 到 max_move 的范围内，防止鼠标移动幅度太大而不稳定
                        dx = np.clip(dx, -max_move, max_move)
                        dy = np.clip(dy, -max_move, max_move)
                        # 使用 win32api.mouse_event 模拟鼠标移动操作
                        # win32con.MOUSEEVENTF_MOVE 表示移动鼠标
                        # -dx 和 dy 是鼠标在水平和垂直方向上的移动距离
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -dx, dy)

                    # 更新上一帧右手食指的位置为当前帧的位置
                    prev_right_index_pos = right_index_pos
                elif handedness == "Left":
                    # 计算左手食指尖在图像中的位置
                    index_finger_tip_left = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame.shape[1], hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame.shape[0]
                    # 计算左手中指尖在图像中的位置
                    middle_finger_tip_left = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * frame.shape[1], hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * frame.shape[0]
                    # 计算左手食指尖和左手中指尖之间的距离
                    # 使用欧几里得距离公式，即 sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    distance = np.sqrt((index_finger_tip_left[0] - middle_finger_tip_left[0])**2 + (index_finger_tip_left[1] - middle_finger_tip_left[1])**2)
                    # 设置一个阈值，可根据实际情况调整
                    threshold_distance = 30
                    if distance < threshold_distance:
                        # 使用 win32api.mouse_event 模拟鼠标左键点击操作
                        # win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP 表示按下并释放鼠标左键
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        # 添加一个时间延迟，防止连续快速点击
                        time.sleep(0.1)

            # 在图像上绘制手部地标和连接，以便可视化手部的位置和形状
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # 在窗口中显示处理后的图像帧
        cv2.imshow('frame', frame)
        # 如果按下 'q' 键，则退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 释放摄像头资源，以便其他程序可以使用摄像头
cap.release()
# 关闭所有 OpenCV 创建的窗口
cv2.destroyAllWindows()