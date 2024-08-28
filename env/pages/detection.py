import os
os.environ['MEDIAPIPE_BINARY_GRAPH_PATH'] = r'D:\EXE\env\exe\Lib\site-packages\mediapipe\modules'
import sys
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model


# Function to correctly handle resource paths when bundled into an executable
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DetectionPage(ctk.CTkFrame):
    def __init__(self, parent, controller, model=None):
        super().__init__(parent)
        self.controller = controller
        self.model = model

        # Setup the main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Setup the video display
        self.video_label = ctk.CTkLabel(self)
        self.video_label.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")

        # Setup the label output
        self.label_output = ctk.CTkLabel(self, text="", font=("Arial", 18))
        self.label_output.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")

        # Initialize variables
        self.cap = None
        self.running = False
        self.sequence = []
        self.sentence = []
        self.predictions = []
        self.threshold = 0.5
        self.actions = np.array(['tea','sugar','coffee','please','sorry', 'milk', 'hello', 'black', 'green'])

        # Set up MediaPipe
        self.mp_holistic = mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # Load the TensorFlow model
        self.model = load_model(resource_path('action.h5'))

    def extract_keypoints(self, results):
        pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
        face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
        lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
        rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
        return np.concatenate([pose, face, lh, rh])

    def start_camera(self):
        if not self.running:
            self.running = True
            self.cap = cv2.VideoCapture(0)
            self.update_frame()

    def stop_camera(self):
        if self.running:
            self.running = False
            if self.cap:
                self.cap.release()
            self.cap = None

    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_holistic.process(image_rgb)

        # Draw landmarks
        self.mp_drawing.draw_landmarks(frame, results.face_landmarks, mp.solutions.holistic.FACEMESH_CONTOURS)
        self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp.solutions.holistic.POSE_CONNECTIONS)
        self.mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp.solutions.holistic.HAND_CONNECTIONS)
        self.mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp.solutions.holistic.HAND_CONNECTIONS)

        # Prediction logic
        keypoints = self.extract_keypoints(results)
        self.sequence.append(keypoints)
        self.sequence = self.sequence[-30:]

        if len(self.sequence) == 30:
            res = self.model.predict(np.expand_dims(self.sequence, axis=0))[0]
            self.predictions.append(np.argmax(res))

            if np.unique(self.predictions[-10:])[0] == np.argmax(res):
                if res[np.argmax(res)] > self.threshold:
                    if len(self.sentence) > 0:
                        if self.actions[np.argmax(res)] != self.sentence[-1]:
                            self.sentence.append(self.actions[np.argmax(res)])
                    else:
                        self.sentence.append(self.actions[np.argmax(res)])

            if len(self.sentence) > 5:
                self.sentence = self.sentence[-5:]

        # Update the label output with the detected action
        self.label_output.configure(text=' '.join(self.sentence))

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        if self.running:
            self.video_label.after(16, self.update_frame)  # 16ms delay for approximately 60 FPS

    def on_show(self):
        self.start_camera()

    def on_hide(self):
        self.stop_camera()
