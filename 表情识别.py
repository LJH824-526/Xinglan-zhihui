# 导入必要的库
import cv2  # OpenCV库，用于计算机视觉任务
import mediapipe as mp  # Mediapipe库，用于实时手部检测

# 初始化 MediaPipe 的手部检测模块
mp_hands = mp.solutions.hands  # 获取手部检测模块
mp_drawing = mp.solutions.drawing_utils  # 导入绘图工具，用于绘制手部关键点和连接线
hands = mp_hands.Hands()  # 创建手部检测对象

# 使用摄像头进行捕获
cap = cv2.VideoCapture(0)  # 打开默认摄像头（0表示第一个摄像头）

# 循环，直到摄像头关闭
while cap.isOpened():
    ret, frame = cap.read()  # 读取一帧图像
    if not ret:  # 如果未成功读取图像，则退出循环
        break

    # 翻转图像（实现镜像效果）并转换色彩空间为 RGB
    frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)  # 处理图像，进行手部检测

    # 转换回 BGR 格式（OpenCV 默认格式）
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    # 绘制手部关键点
    if results.multi_hand_landmarks:  # 如果检测到多只手的关键点
        for hand_landmarks in results.multi_hand_landmarks:  # 遍历每只手
            # 使用绘图工具绘制手的关键点及其连接线
            mp_drawing.draw_landmarks(frame_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 显示处理后的图像窗口
    cv2.imshow('MediaPipe Hand Tracking', frame_bgr)

    # 按下 'q' 键退出循环
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# 释放摄像头资源并关闭所有OpenCV创建的窗口
cap.release()
cv2.destroyAllWindows()