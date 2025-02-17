import cv2
import mediapipe as mp
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier


import os
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns



# MediaPipe 손 모듈 초기화
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 각 제스처에 대한 폴더명과 레이블을 매핑합니다.
gesture_folders = {
    'none': 0,
    'rock': 1,
    'paper': 2,
    'scissors': 3
}

# 각도를 계산하는 함수
def calculate_angles(hand_landmarks, image_width, image_height):
    joint = np.zeros((21, 3))
    for j, lm in enumerate(hand_landmarks.landmark):
        joint[j] = [lm.x * image_width, lm.y * image_height, lm.z]

    # 벡터 계산
    v1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 0, 13, 14, 15, 0, 17, 18, 19], :]
    v2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], :]
    v = v2 - v1  # 벡터
    v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

    # 각도 계산
    angle = np.arccos(np.einsum('nt,nt->n',
                                v[[0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18], :],
                                v[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :]))  # 내적
    angle = np.degrees(angle)  # 라디안을 도로 변환

    return angle

# 이미지에서 특징(각도)와 레이블을 추출하는 함수
def extract_features_and_labels():
    with mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5) as hands:
        features = []
        labels = []
        for gesture_name, label in gesture_folders.items():
            folder_path = os.path.join('rps_data_sample', gesture_name)
            for img_name in os.listdir(folder_path):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(folder_path, img_name)
                    img = cv2.imread(img_path)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    results = hands.process(img)
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            angles = calculate_angles(hand_landmarks, img.shape[1], img.shape[0])
                            if angles is not None:
                                features.append(angles)
                                labels.append(label)
        return np.array(features), np.array(labels)

# 특징과 레이블 추출
features, labels = extract_features_and_labels()
# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)



# KNN 모델 훈련
# knn = KNeighborsClassifier(n_neighbors=3)
# knn.fit(X_train, y_train)
#
# accuracy = knn.score(X_test, y_test)
# y_pred = knn.predict(X_test)


# dt = DecisionTreeClassifier(random_state=42)
# dt.fit(X_train, y_train)
#
# accuracy = dt.score(X_test, y_test)
# y_pred = dt.predict(X_test)

# svm = SVC(kernel='linear', C=1.0, random_state=42)
# svm.fit(X_train, y_train)
#
# accuracy = svm.score(X_test, y_test)
# y_pred = svm.predict(X_test)
#
# rf = RandomForestClassifier(n_estimators=100, random_state=42)
# rf.fit(X_train, y_train)
#
# accuracy = rf.score(X_test, y_test)
# y_pred = rf.predict(X_test)

mlp = MLPClassifier(hidden_layer_sizes=(100,), max_iter=300, alpha=0.0001,
                    solver='adam', random_state=42)
mlp.fit(X_train, y_train)

accuracy = mlp.score(X_test, y_test)
y_pred = mlp.predict(X_test)

print(f'Test Accuracy: {accuracy:.4f}')

cm = confusion_matrix(y_test, y_pred)
# 혼동 행렬 시각화
plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt="d", cmap='Blues', xticklabels=gesture_folders.keys(), yticklabels=gesture_folders.keys())
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()

# # 실시간 비디오 스트림 처리를 위한 MediaPipe 손 설정
# video = cv2.VideoCapture(0)
# with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
#     while video.isOpened():
#         ret, img = video.read()
#         if not ret:
#             break
#         img = cv2.flip(img, 1)
#         img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         results = hands.process(img_rgb)
#
#         if results.multi_hand_landmarks:
#             for hand_landmarks in results.multi_hand_landmarks:
#                 angles = calculate_angles(hand_landmarks, img.shape[1], img.shape[0])
#                 X_pred = np.array([angles], dtype=np.float32)
#                 gesture_id = knn.predict(X_pred)[0]
#                 gesture_name = [name for name, idx in gesture_folders.items() if idx == gesture_id][0]
#                 print(gesture_name)
#                 mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
#
#         cv2.imshow('Hand Gesture Recognition', img)
#         if cv2.waitKey(5) & 0xFF == 27:  # ESC 키로 종료
#             break
#
# video.release()
# cv2.destroyAllWindows()