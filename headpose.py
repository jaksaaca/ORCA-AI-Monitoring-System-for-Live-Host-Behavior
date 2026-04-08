import cv2
import mediapipe as mp
import numpy as np


class HeadPoseEstimator:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def get_pose(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.mesh.process(rgb)

        if not result.multi_face_landmarks:
            return None

        face = result.multi_face_landmarks[0].landmark

        def pt(i):
            return np.array([face[i].x * w, face[i].y * h], dtype=np.float32)

        left_eye = pt(33)
        right_eye = pt(263)
        nose = pt(1)
        chin = pt(152)

        eye_center = (left_eye + right_eye) / 2.0

        face_width = np.linalg.norm(right_eye - left_eye)
        face_height = np.linalg.norm(chin - eye_center)

        if face_width < 1 or face_height < 1:
            return None

        # yaw: hidung geser kiri/kanan dari tengah mata
        yaw = ((nose[0] - eye_center[0]) / face_width) * 100.0

        # pitch: makin besar = makin turun
        pitch = ((nose[1] - eye_center[1]) / face_height) * 100.0

        # roll: kemiringan garis mata
        dy = right_eye[1] - left_eye[1]
        dx = right_eye[0] - left_eye[0]
        roll = float(np.degrees(np.arctan2(dy, dx)))

        return float(pitch), float(yaw), float(roll)