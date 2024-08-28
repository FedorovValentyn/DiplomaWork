from PIL import Image, ImageTk
import customtkinter as ctk
import cv2
import numpy as np
import mediapipe as mp
import os
os.environ['MEDIAPIPE_BINARY_GRAPH_PATH'] = r'D:\EXE\env\exe\Lib\site-packages\mediapipe\modules'
import sys


class DetectionPage(ctk.CTkFrame):
    def __init__(self, parent, controller, model, actions):
        super().__init__(parent)
        self.controller = controller
        self.model = model
        self.actions = actions

        # Initialize variables for detection
        self.sequence = []
        self.sentence = []
        self.predictions = []
        self.threshold = 0.99

        # Initialize video capture
        self.cap = cv2.VideoCapture(0)

        # Set up Mediapipe model
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(min_detection_confidence=0.8, min_tracking_confidence=0.79)

        # Create a frame for the video and labels
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Create a label to display the video feed
        self.video_label = ctk.CTkLabel(self.main_frame)
        self.video_label.pack(side="left", fill="both", expand=True)

        # Create a frame for the output labels
        self.output_frame = ctk.CTkFrame(self.main_frame, width=300)  # Adjust width as needed
        self.output_frame.pack(side="right", fill="y", padx=10, pady=10)

        # Create a textbox to show the detected actions
        self.textbox = ctk.CTkTextbox(self.output_frame, wrap="word", font=("Arial", 20))
        self.textbox.pack(expand=True, fill="both")
        self.textbox.insert("end", "Detected Actions:\n")

    def update_frame(self):
        # Read frame from video capture
        ret, frame = self.cap.read()
        if not ret:
            return

        # Make detections
        image, results = self.mediapipe_detection(frame)

        # Draw landmarks
        self.draw_styled_landmarks(image, results)

        # Prediction logic
        keypoints = self.extract_keypoints(results)
        self.sequence.append(keypoints)
        self.sequence = self.sequence[-30:]

        if len(self.sequence) == 30:
            res = self.model.predict(np.expand_dims(self.sequence, axis=0))[0]
            self.predictions.append(np.argmax(res))

            # Only add to sentence if confidence is high enough
            if np.unique(self.predictions[-10:])[0] == np.argmax(res):
                if res[np.argmax(res)] > self.threshold:
                    current_action = self.actions[np.argmax(res)]
                    if len(self.sentence) > 0:
                        if current_action != self.sentence[-1]:
                            self.sentence.append(current_action)
                            self.append_to_textbox(current_action)
                    else:
                        self.sentence.append(current_action)
                        self.append_to_textbox(current_action)

            if len(self.sentence) > 5:
                self.sentence = self.sentence[-5:]

        # Display the most recent detected action
        if len(self.sentence) > 0:
            cv2.rectangle(image, (0, image.shape[0] - 40), (640, image.shape[0]), (245, 117, 16), -1)
            cv2.putText(image, self.sentence[-1], (3, image.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Convert image to RGB (OpenCV uses BGR by default)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        img = Image.fromarray(image)

        # Convert to ImageTk format
        img_tk = ImageTk.PhotoImage(image=img)

        # Update the video_label with the new image
        self.video_label.configure(image=img_tk)
        self.video_label.image = img_tk  # Keep reference to avoid garbage collection

    def mediapipe_detection(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.holistic.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image, results

    def draw_styled_landmarks(self, image, results):
        mp_drawing = mp.solutions.drawing_utils

        # Draw pose landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
            )

        # Draw face landmarks
        if results.face_landmarks:
            mp_drawing.draw_landmarks(
                image, results.face_landmarks, self.mp_holistic.FACEMESH_TESSELATION,
                mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
            )

        # Draw left hand landmarks
        if results.left_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
            )

        # Draw right hand landmarks
        if results.right_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

    def extract_keypoints(self, results):
        pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                         results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
        face = np.array([[res.x, res.y, res.z] for res in
                         results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468 * 3)
        lh = np.array([[res.x, res.y, res.z] for res in
                       results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(
            21 * 3)
        rh = np.array([[res.x, res.y, res.z] for res in
                       results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(
            21 * 3)
        return np.concatenate([pose, face, lh, rh])

    def append_to_textbox(self, text):
        # Append text to the textbox with a newline
        self.textbox.configure(state="normal")  # Allow editing
        self.textbox.insert("end", f"{text}\n")
        self.textbox.configure(state="disabled")  # Disable editing
        self.textbox.yview("end")  # Scroll to the end

    def on_hide(self):
        # Release the video capture when the page is hidden
        if self.cap.isOpened():
            self.cap.release()

    def on_show(self):
        # Reopen video capture when the page is shown
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
