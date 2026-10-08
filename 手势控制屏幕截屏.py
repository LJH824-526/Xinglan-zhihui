import cv2
import numpy as np
import pyautogui
import time
import os


# 计算轮廓的近似多边形拟合后的顶点数量（用于简单判断形状是否类似握拳）
def count_approx_vertices(contour):
    epsilon = 0.01 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    return len(approx)


# 定义截屏函数，添加异常处理机制确保截屏更稳定，并修改保存路径
def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        file_name = f"screenshot_{timestamp}.png"
        # 指定保存截图的文件夹路径
        save_path = r"C:\Users\slk\Pictures\Screenshots"
        # 判断保存路径的文件夹是否存在，不存在则创建
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, file_name)
        cv2.imwrite(file_path, screenshot)
        print(f"截屏已成功保存为 {file_path}")
    except Exception as e:
        print(f"截屏时出现错误: {str(e)}")


# 打开摄像头
cap = cv2.VideoCapture(0)

# 用于控制截屏操作的间隔时间，避免短时间内多次重复截屏（单位：秒）
screenshot_interval = 2
last_screenshot_time = time.time()

while True:
    # 读取摄像头帧
    ret, frame = cap.read()
    if not ret:
        break

    # 转换为灰度图像，便于后续处理
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 进行高斯模糊，减少噪声影响
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # 通过阈值处理得到二值图像，方便提取轮廓
    _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 寻找轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # 计算轮廓面积，过滤掉过小的轮廓（可能是噪声等干扰）
        area = cv2.contourArea(contour)
        if area < 1000:
            continue

        # 计算轮廓的外接矩形，获取其宽高比等信息（可以辅助判断手势形状）
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)

        # 简单通过外接矩形宽高比以及轮廓近似顶点数量来判断是否类似握拳手势（可调整阈值和条件）
        if 0.8 < aspect_ratio < 1.2 and count_approx_vertices(contour) < 10:
            current_time = time.time()
            if current_time - last_screenshot_time >= screenshot_interval:
                take_screenshot()
                last_screenshot_time = current_time
                break

    # 显示摄像头画面
    cv2.imshow("Camera Feed", frame)
    key = cv2.waitKey(1)
    if key == 27:  # 按ESC键退出循环
        break

cap.release()
cv2.destroyAllWindows()