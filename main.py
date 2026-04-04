import cv2
import time
import config

from detector import FaceDetector
from headpose import HeadPoseEstimator
from smoother import Smoother
from classifier import BehaviorClassifier
from logger import Logger

cap = cv2.VideoCapture(config.CAMERA_INDEX)

detector = FaceDetector()
pose = HeadPoseEstimator()
smooth = Smoother(config.SMOOTH_WINDOW)
clf = BehaviorClassifier(config)
logger = Logger(f"logs/{config.SESSION_ID}.csv")

frame_count = 0
last_log_time = 0

is_running = False   # 🔥 control state

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # UI STATUS
    status_text = "PAUSED"
    color = (0, 0, 255)

    if is_running:

        status_text = "RUNNING"
        color = (0, 255, 0)

        if frame_count % config.PROCESS_EVERY_N_FRAMES != 0:
            continue

        face, _ = detector.detect(frame)

        if face:
            pose_data = pose.get_pose(frame)
        else:
            pose_data = None

        if pose_data:
            pitch, yaw, roll = pose_data
            smooth.update(pitch, yaw, roll)
            pitch, yaw, roll = smooth.get()
        else:
            pitch, yaw, roll = 0, 0, 0

        status = clf.update(face, pitch, yaw)

        now = time.time()
        if now - last_log_time >= 1:
            logger.log(face, pitch, yaw, roll, status)
            last_log_time = now

        cv2.putText(frame, status, (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)

    # UI Overlay
    cv2.putText(frame, f"System: {status_text}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.putText(frame, "S:Start | P:Pause | Q:Quit", (30, 440),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)

    cv2.imshow("Host Monitoring", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        is_running = True

    elif key == ord('p'):
        is_running = False

    elif key == ord('q'):
        break

cap.release()
logger.close()
cv2.destroyAllWindows()