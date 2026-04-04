import cv2
import mediapipe as mp
import numpy as np

class HeadPoseEstimator:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)

    def get_pose(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.mesh.process(rgb)

        if not result.multi_face_landmarks:
            return None

        face = result.multi_face_landmarks[0]

        # titik penting
        idx = [33, 263, 1, 61, 291, 199]

        face_2d = []
        face_3d = []

        for i in idx:
            lm = face.landmark[i]
            x, y = int(lm.x * w), int(lm.y * h)

            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])

        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)

        focal_length = w
        cam_matrix = np.array([
            [focal_length, 0, w/2],
            [0, focal_length, h/2],
            [0, 0, 1]
        ])

        dist_matrix = np.zeros((4, 1))

        success, rot_vec, trans_vec = cv2.solvePnP(
            face_3d, face_2d, cam_matrix, dist_matrix
        )

        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        pitch, yaw, roll = angles

        return pitch * 360, yaw * 360, roll * 360