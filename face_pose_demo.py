import cv2
import mediapipe as mp
import numpy as np

# 初始化 MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# 打开摄像头
cap = cv2.VideoCapture(0)

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("错误：无法打开摄像头。")
    exit()

print("摄像头已启动。请正对摄像头。按 'q' 键退出。")
print("-" * 30)

# 瞳孔追踪变量
left_pupil_history = []
right_pupil_history = []
max_history = 30  # 保留最近30帧的瞳孔位置

# MediaPipe 虹膜关键点索引
LEFT_IRIS = [468, 469, 470, 471, 472]  # 左眼虹膜5个点
RIGHT_IRIS = [473, 474, 475, 476, 477]  # 右眼虹膜5个点

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("忽略空的摄像头帧。")
        continue

    # 获取图像尺寸，用于 3D 姿态估计
    image_h, image_w, _ = image.shape

    # 为了提高性能，将图像标记为不可写
    image.flags.writeable = False
    # 将 BGR 图像转换为 RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 翻转图像（自拍视角）
    image_rgb = cv2.flip(image_rgb, 1)

    # 处理图像并找到面部关键点
    results = face_mesh.process(image_rgb)

    # 将 RGB 图像转回 BGR 并翻转回来，用于显示
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    # 状态文本
    head_pose_status = "FACE NOT FOUND"
    eye_status = ""

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            
            # --- 瞳孔/虹膜检测与追踪 ---
            # 获取左眼虹膜中心（取5个点的平均值）
            left_iris_x = sum([face_landmarks.landmark[i].x for i in LEFT_IRIS]) / len(LEFT_IRIS)
            left_iris_y = sum([face_landmarks.landmark[i].y for i in LEFT_IRIS]) / len(LEFT_IRIS)
            left_iris_center = (int(left_iris_x * image_w), int(left_iris_y * image_h))
            
            # 获取右眼虹膜中心
            right_iris_x = sum([face_landmarks.landmark[i].x for i in RIGHT_IRIS]) / len(RIGHT_IRIS)
            right_iris_y = sum([face_landmarks.landmark[i].y for i in RIGHT_IRIS]) / len(RIGHT_IRIS)
            right_iris_center = (int(right_iris_x * image_w), int(right_iris_y * image_h))
            
            # 保存瞳孔历史位置
            left_pupil_history.append(left_iris_center)
            right_pupil_history.append(right_iris_center)
            
            # 限制历史记录长度
            if len(left_pupil_history) > max_history:
                left_pupil_history.pop(0)
            if len(right_pupil_history) > max_history:
                right_pupil_history.pop(0)
            
            # 绘制瞳孔位置（大圆点）
            cv2.circle(image, left_iris_center, 3, (0, 255, 255), -1)  # 黄色
            cv2.circle(image, right_iris_center, 3, (0, 255, 255), -1)
            
            # 绘制瞳孔移动轨迹
            for i in range(1, len(left_pupil_history)):
                # 线条透明度随时间衰减
                alpha = int(255 * (i / len(left_pupil_history)))
                color = (0, alpha, alpha)
                cv2.line(image, left_pupil_history[i-1], left_pupil_history[i], color, 2)
            
            for i in range(1, len(right_pupil_history)):
                alpha = int(255 * (i / len(right_pupil_history)))
                color = (0, alpha, alpha)
                cv2.line(image, right_pupil_history[i-1], right_pupil_history[i], color, 2)
            
            # 计算瞳孔移动速度（如果有足够的历史数据）
            if len(left_pupil_history) > 5:
                # 计算最近5帧的移动距离
                left_movement = np.sqrt(
                    (left_pupil_history[-1][0] - left_pupil_history[-5][0])**2 +
                    (left_pupil_history[-1][1] - left_pupil_history[-5][1])**2
                )
                right_movement = np.sqrt(
                    (right_pupil_history[-1][0] - right_pupil_history[-5][0])**2 +
                    (right_pupil_history[-1][1] - right_pupil_history[-5][1])**2
                )
                avg_movement = (left_movement + right_movement) / 2
                
                if avg_movement > 10:
                    eye_status = f"EYE MOVEMENT: HIGH ({avg_movement:.1f}px)"
                elif avg_movement > 5:
                    eye_status = f"EYE MOVEMENT: MEDIUM ({avg_movement:.1f}px)"
                else:
                    eye_status = f"EYE MOVEMENT: STABLE ({avg_movement:.1f}px)"
            
            # --- 核心：3D头部姿态估计 ---
            
            # 这是 478 个关键点中的 6 个标准点，用于姿态估计
            # (鼻尖, 下巴, 左眼角, 右眼角, 左嘴角, 右嘴角)
            landmarks_3d = np.array([
                [0.0, 0.0, 0.0],    # 鼻尖 (Landmark 1)
                [0.0, -330.0, -65.0], # 下巴 (Landmark 152)
                [-225.0, 170.0, -135.0], # 左眼角 (Landmark 263)
                [225.0, 170.0, -135.0],  # 右眼角 (Landmark 33)
                [-150.0, -150.0, -125.0], # 左嘴角 (Landmark 287)
                [150.0, -150.0, -125.0]   # 右嘴角 (Landmark 57)
            ], dtype=np.float64)
            
            # 从 MediaPipe 结果中获取对应的 2D 像素坐标
            try:
                landmarks_2d = np.array([
                    [face_landmarks.landmark[1].x * image_w, face_landmarks.landmark[1].y * image_h],
                    [face_landmarks.landmark[152].x * image_w, face_landmarks.landmark[152].y * image_h],
                    [face_landmarks.landmark[263].x * image_w, face_landmarks.landmark[263].y * image_h],
                    [face_landmarks.landmark[33].x * image_w, face_landmarks.landmark[33].y * image_h],
                    [face_landmarks.landmark[287].x * image_w, face_landmarks.landmark[287].y * image_h],
                    [face_landmarks.landmark[57].x * image_w, face_landmarks.landmark[57].y * image_h],
                ], dtype=np.float64)
            except Exception as e:
                # 如果关键点索引不存在则跳过
                print("关键点索引错误：", e)
                continue

            # 估计相机参数 (假设)
            focal_length = 1 * image_w
            cam_center = (image_w / 2, image_h / 2)
            camera_matrix = np.array([
                [focal_length, 0, cam_center[0]],
                [0, focal_length, cam_center[1]],
                [0, 0, 1]
            ], dtype=np.float64)
            
            # 假设没有镜头畸变
            dist_coeffs = np.zeros((4, 1), dtype=np.float64)
            
            # --- 关键函数：solvePnP ---
            (success_pnp, rotation_vector, translation_vector) = cv2.solvePnP(
                landmarks_3d, landmarks_2d, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
            )

            if success_pnp:
                x_angle = rotation_vector[0][0] * (180 / np.pi)
                y_angle = rotation_vector[1][0] * (180 / np.pi)
                z_angle = rotation_vector[2][0] * (180 / np.pi)

                # --- 解读姿态 ---
                if x_angle > 15:
                    head_pose_status = "LOOKING: DOWN (Distracted?)"
                elif x_angle < -15:
                    head_pose_status = "LOOKING: UP"
                elif y_angle > 20:
                    head_pose_status = "LOOKING: RIGHT (Distracted?)"
                elif y_angle < -20:
                    head_pose_status = "LOOKING: LEFT (Distracted?)"
                else:
                    head_pose_status = "LOOKING: STRAIGHT"

            # (可选) 在脸上绘制面部网格
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec)

    # 在屏幕上显示状态
    cv2.putText(image, head_pose_status, (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    
    # 显示瞳孔移动状态
    if eye_status:
        cv2.putText(image, eye_status, (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
    
    # 显示图像
    cv2.imshow('MediaPipe Head Pose + Pupil Tracking (Press q to quit)', image)

    # 按 'q' 键退出循环
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
face_mesh.close()
print("-" * 30)
print("测试结束。")
