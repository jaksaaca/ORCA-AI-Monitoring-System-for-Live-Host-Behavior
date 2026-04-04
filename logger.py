import csv
import os
from config import STUDIO_ID, SESSION_ID
from utils.time_utils import get_iso_time

class Logger:
    def __init__(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        self.filename = filename
        self.file = open(filename, "w", newline="", buffering=1)
        self.writer = csv.writer(self.file)

        # Header CSV
        self.writer.writerow([
            "timestamp",
            "studio_id",
            "session_id",
            "face_detected",
            "pitch",
            "yaw",
            "roll",
            "status"
        ])

        # Counter summary
        self.total = 0
        self.face_count = 0
        self.facing_count = 0
        self.head_down_count = 0
        self.off_frame_count = 0
        self.not_facing_count = 0

    def log(self, face, pitch, yaw, roll, status):
        self.writer.writerow([
            get_iso_time(),
            STUDIO_ID,
            SESSION_ID,
            face,
            round(pitch, 2),
            round(yaw, 2),
            round(roll, 2),
            status
        ])

        # Update counter
        self.total += 1

        if face:
            self.face_count += 1

        if status == "facing_camera":
            self.facing_count += 1

        elif status == "head_down":
            self.head_down_count += 1

        elif status == "off_frame":
            self.off_frame_count += 1

        elif status == "not_facing_camera":
            self.not_facing_count += 1

    def close(self):
        if self.total == 0:
            self.file.close()
            return

        # Hitung persen
        face_pct = (self.face_count / self.total) * 100
        facing_pct = (self.facing_count / self.total) * 100
        head_down_pct = (self.head_down_count / self.total) * 100
        off_frame_pct = (self.off_frame_count / self.total) * 100
        not_facing_pct = (self.not_facing_count / self.total) * 100

        self.file.close()

        # =========================
        # 🔥 WRITE SUMMARY TXT
        # =========================
        summary_path = self.filename.replace(".csv", "_summary.txt")

        with open(summary_path, "w") as f:
            f.write("===== SESSION SUMMARY =====\n")
            f.write(f"Studio ID   : {STUDIO_ID}\n")
            f.write(f"Session ID  : {SESSION_ID}\n\n")

            f.write(f"Total Duration     : {self.total} sec\n\n")

            f.write("=== BEHAVIOR ===\n")
            f.write(f"Face Presence      : {face_pct:.2f}%\n")
            f.write(f"Facing Camera      : {facing_pct:.2f}%\n")
            f.write(f"Head Down          : {head_down_pct:.2f}%\n")
            f.write(f"Not Facing         : {not_facing_pct:.2f}%\n")
            f.write(f"Off Frame          : {off_frame_pct:.2f}%\n")

        print(f"[SUMMARY SAVED] {summary_path}")