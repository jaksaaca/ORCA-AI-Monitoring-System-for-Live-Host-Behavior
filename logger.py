import csv
import os
from config import STUDIO_ID, SESSION_ID
from utils.time_utils import get_iso_time, get_readable_time


class Logger:
    def __init__(self, filename):
        self.filename = filename

        self.start_time = get_readable_time()

        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        file_exists = os.path.isfile(filename)

        self.file = open(filename, "a", newline="", buffering=1)
        self.writer = csv.writer(self.file)

        if not file_exists:
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

        self.total = 0
        self.face_count = 0
        self.facing_count = 0
        self.head_down_count = 0
        self.off_frame_count = 0
        self.not_facing_count = 0

    def log(self, face, pitch, yaw, roll, status):
        pitch = round(pitch, 2) if pitch is not None else 0
        yaw = round(yaw, 2) if yaw is not None else 0
        roll = round(roll, 2) if roll is not None else 0

        self.writer.writerow([
            get_iso_time(),
            STUDIO_ID,
            SESSION_ID,
            face,
            pitch,
            yaw,
            roll,
            status
        ])

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

        end_time = get_readable_time()
        session_time = f"{self.start_time} - {end_time}"

        face_pct = (self.face_count / self.total) * 100
        facing_pct = (self.facing_count / self.total) * 100
        head_down_pct = (self.head_down_count / self.total) * 100
        off_frame_pct = (self.off_frame_count / self.total) * 100
        not_facing_pct = (self.not_facing_count / self.total) * 100

        self.file.close()

        summary_file = "logs/summary.csv"
        file_exists = os.path.isfile(summary_file)

        with open(summary_file, "a", newline="") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow([
                    "session_time",
                    "studio_id",
                    "session_id",
                    "duration_frames",
                    "face_pct",
                    "facing_pct",
                    "head_down_pct",
                    "not_facing_pct",
                    "off_frame_pct"
                ])

            writer.writerow([
                session_time,
                STUDIO_ID,
                SESSION_ID,
                self.total,
                round(face_pct, 2),
                round(facing_pct, 2),
                round(head_down_pct, 2),
                round(not_facing_pct, 2),
                round(off_frame_pct, 2)
            ])

        print("[SUMMARY CSV UPDATED] summary.csv")

        txt_file = "logs/summary.txt"
        with open(txt_file, "a") as f:
            f.write("===== SESSION =====\n")
            f.write(f"Time           : {session_time}\n")
            f.write(f"Studio ID      : {STUDIO_ID}\n")
            f.write(f"Session ID     : {SESSION_ID}\n")
            f.write(f"Duration       : {self.total} sec\n\n")

            f.write("=== BEHAVIOR ===\n")
            f.write(f"Face Presence  : {face_pct:.2f}%\n")
            f.write(f"Facing Camera  : {facing_pct:.2f}%\n")
            f.write(f"Head Down      : {head_down_pct:.2f}%\n")
            f.write(f"Not Facing     : {not_facing_pct:.2f}%\n")
            f.write(f"Off Frame      : {off_frame_pct:.2f}%\n")
            f.write("\n============================\n\n")

        print("[SUMMARY TXT UPDATED] summary.txt")