import csv
import os
from datetime import datetime


class Logger:
    def __init__(self, studio_id, host_name, location):
        self.studio_id = studio_id
        self.host_name = host_name
        self.location = location

        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)

        # =========================
        # 1) CURRENT SESSION LOG
        # reset setiap mulai sesi
        # =========================
        self.session_log_file = os.path.join(self.logs_dir, "current_session_log.csv")

        self.start_dt = datetime.now()
        self.start_date_str = self.start_dt.strftime("%d %b %Y")
        self.start_day_str = self.start_dt.strftime("%A")
        self.start_time_str = self.start_dt.strftime("%H.%M")

        self.total_seconds = 0
        self.face_detected_seconds = 0
        self.facing_camera_seconds = 0
        self.head_down_seconds = 0
        self.not_facing_seconds = 0
        self.off_frame_seconds = 0

        self.session_file = open(self.session_log_file, "w", newline="", encoding="utf-8")
        self.session_writer = csv.writer(self.session_file)
        self.session_writer.writerow([
            "timestamp",
            "date",
            "day",
            "time",
            "host_name",
            "studio_id",
            "location",
            "face_detected",
            "pitch",
            "yaw",
            "roll",
            "status"
        ])

    def log(self, face, pitch, yaw, roll, status):
        now = datetime.now()

        pitch = round(pitch, 2) if pitch is not None else 0
        yaw = round(yaw, 2) if yaw is not None else 0
        roll = round(roll, 2) if roll is not None else 0

        self.session_writer.writerow([
            now.strftime("%Y-%m-%d %H:%M:%S"),
            now.strftime("%d %b %Y"),
            now.strftime("%A"),
            now.strftime("%H.%M"),
            self.host_name,
            self.studio_id,
            self.location,
            face,
            pitch,
            yaw,
            roll,
            status
        ])

        self.total_seconds += 1

        if face:
            self.face_detected_seconds += 1

        if status == "facing_camera":
            self.facing_camera_seconds += 1
        elif status == "head_down":
            self.head_down_seconds += 1
        elif status == "not_facing_camera":
            self.not_facing_seconds += 1
        elif status == "off_frame":
            self.off_frame_seconds += 1

    def close(self):
        self.session_file.close()

        if self.total_seconds == 0:
            return

        end_dt = datetime.now()
        end_time_str = end_dt.strftime("%H.%M")
        live_time_range = f"{self.start_time_str} - {end_time_str}"

        face_pct = self._pct(self.face_detected_seconds, self.total_seconds)
        facing_pct = self._pct(self.facing_camera_seconds, self.total_seconds)
        head_down_pct = self._pct(self.head_down_seconds, self.total_seconds)
        not_facing_pct = self._pct(self.not_facing_seconds, self.total_seconds)
        off_frame_pct = self._pct(self.off_frame_seconds, self.total_seconds)

        self._write_session_summary(
            date_str=self.start_date_str,
            day_str=self.start_day_str,
            start_time=self.start_time_str,
            end_time=end_time_str,
            live_time_range=live_time_range,
            face_pct=face_pct,
            facing_pct=facing_pct,
            head_down_pct=head_down_pct,
            not_facing_pct=not_facing_pct,
            off_frame_pct=off_frame_pct
        )

        self._update_host_location_rollup()

    def _write_session_summary(
        self,
        date_str,
        day_str,
        start_time,
        end_time,
        live_time_range,
        face_pct,
        facing_pct,
        head_down_pct,
        not_facing_pct,
        off_frame_pct
    ):
        summary_file = os.path.join(self.logs_dir, "session_summary.csv")
        file_exists = os.path.isfile(summary_file)

        with open(summary_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow([
                    "date",
                    "day",
                    "live_start",
                    "live_end",
                    "live_time_range",
                    "host_name",
                    "studio_id",
                    "location",
                    "total_duration_seconds",

                    "face_detected_seconds",
                    "face_detected_pct",

                    "facing_camera_seconds",
                    "facing_camera_pct",

                    "head_down_seconds",
                    "head_down_pct",

                    "not_facing_seconds",
                    "not_facing_pct",

                    "off_frame_seconds",
                    "off_frame_pct"
                ])

            writer.writerow([
                date_str,
                day_str,
                start_time,
                end_time,
                live_time_range,
                self.host_name,
                self.studio_id,
                self.location,
                self.total_seconds,

                self.face_detected_seconds,
                face_pct,

                self.facing_camera_seconds,
                facing_pct,

                self.head_down_seconds,
                head_down_pct,

                self.not_facing_seconds,
                not_facing_pct,

                self.off_frame_seconds,
                off_frame_pct
            ])

    def _update_host_location_rollup(self):
        rollup_file = os.path.join(self.logs_dir, "host_location_rollup.csv")

        rows = []
        if os.path.isfile(rollup_file):
            with open(rollup_file, "r", newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))

        target_found = False

        for row in rows:
            if (
                row["host_name"] == self.host_name
                and row["location"] == self.location
                and row["studio_id"] == self.studio_id
            ):
                row["live_count"] = str(int(row["live_count"]) + 1)
                row["total_duration_seconds"] = str(
                    int(row["total_duration_seconds"]) + self.total_seconds
                )
                row["face_detected_seconds"] = str(
                    int(row["face_detected_seconds"]) + self.face_detected_seconds
                )
                row["facing_camera_seconds"] = str(
                    int(row["facing_camera_seconds"]) + self.facing_camera_seconds
                )
                row["head_down_seconds"] = str(
                    int(row["head_down_seconds"]) + self.head_down_seconds
                )
                row["not_facing_seconds"] = str(
                    int(row["not_facing_seconds"]) + self.not_facing_seconds
                )
                row["off_frame_seconds"] = str(
                    int(row["off_frame_seconds"]) + self.off_frame_seconds
                )

                total = int(row["total_duration_seconds"])
                row["face_detected_pct"] = str(self._pct(int(row["face_detected_seconds"]), total))
                row["facing_camera_pct"] = str(self._pct(int(row["facing_camera_seconds"]), total))
                row["head_down_pct"] = str(self._pct(int(row["head_down_seconds"]), total))
                row["not_facing_pct"] = str(self._pct(int(row["not_facing_seconds"]), total))
                row["off_frame_pct"] = str(self._pct(int(row["off_frame_seconds"]), total))

                target_found = True
                break

        if not target_found:
            rows.append({
                "host_name": self.host_name,
                "location": self.location,
                "studio_id": self.studio_id,
                "live_count": "1",
                "total_duration_seconds": str(self.total_seconds),
                "face_detected_seconds": str(self.face_detected_seconds),
                "face_detected_pct": str(self._pct(self.face_detected_seconds, self.total_seconds)),
                "facing_camera_seconds": str(self.facing_camera_seconds),
                "facing_camera_pct": str(self._pct(self.facing_camera_seconds, self.total_seconds)),
                "head_down_seconds": str(self.head_down_seconds),
                "head_down_pct": str(self._pct(self.head_down_seconds, self.total_seconds)),
                "not_facing_seconds": str(self.not_facing_seconds),
                "not_facing_pct": str(self._pct(self.not_facing_seconds, self.total_seconds)),
                "off_frame_seconds": str(self.off_frame_seconds),
                "off_frame_pct": str(self._pct(self.off_frame_seconds, self.total_seconds)),
            })

        with open(rollup_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "host_name",
                "location",
                "studio_id",
                "live_count",
                "total_duration_seconds",
                "face_detected_seconds",
                "face_detected_pct",
                "facing_camera_seconds",
                "facing_camera_pct",
                "head_down_seconds",
                "head_down_pct",
                "not_facing_seconds",
                "not_facing_pct",
                "off_frame_seconds",
                "off_frame_pct"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _pct(value, total):
        if total == 0:
            return 0.0
        return round((value / total) * 100, 2)