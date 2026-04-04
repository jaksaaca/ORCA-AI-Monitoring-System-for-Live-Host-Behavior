import time

class BehaviorClassifier:
    def __init__(self, config):
        self.cfg = config

        self.head_down_counter = 0
        self.off_frame_counter = 0
        self.not_facing_counter = 0

        self.current_state = "face_detected"
        self.last_change_time = time.time()

    def update(self, face_detected, pitch, yaw):
        now = time.time()

        # OFF FRAME
        if not face_detected:
            self.off_frame_counter += 1
        else:
            self.off_frame_counter = 0

        # HEAD DOWN
        if face_detected:

            if pitch < -self.cfg.PITCH_DOWN_STRICT:
                self.head_down_counter += 2

            elif pitch < -self.cfg.PITCH_DOWN_START:
                self.head_down_counter += 1

            else:
                self.head_down_counter = max(0, self.head_down_counter - 1)

        else:
            self.head_down_counter = 0

        # NOT FACING
        if face_detected and abs(yaw) > self.cfg.YAW_THRESHOLD:
            self.not_facing_counter += 1
        else:
            self.not_facing_counter = 0

        # convert counter ke detik
        off_frame_sec = self.off_frame_counter / 10
        head_down_sec = self.head_down_counter / 10
        not_facing_sec = self.not_facing_counter / 10

        new_state = self.current_state

        if off_frame_sec > self.cfg.OFF_FRAME_MIN_SECONDS:
            new_state = "off_frame"

        elif head_down_sec > self.cfg.HEAD_DOWN_MIN_SECONDS:
            new_state = "head_down"

        elif not_facing_sec > self.cfg.NOT_FACING_MIN_SECONDS:
            new_state = "not_facing_camera"

        elif face_detected:
            new_state = "facing_camera"

        else:
            new_state = "not_detected"

        # HOLD biar gak flicker
        if new_state != self.current_state:
            if now - self.last_change_time > self.cfg.STATE_HOLD_SECONDS:
                self.current_state = new_state
                self.last_change_time = now

        return self.current_state