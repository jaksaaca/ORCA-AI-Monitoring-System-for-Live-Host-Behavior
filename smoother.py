from collections import deque
import numpy as np


class Smoother:
    def __init__(self, window=10):
        self.pitch = deque(maxlen=window)
        self.yaw = deque(maxlen=window)
        self.roll = deque(maxlen=window)

    def update(self, p, y, r):
        self.pitch.append(float(p))
        self.yaw.append(float(y))
        self.roll.append(float(r))

    def get(self):
        if len(self.pitch) == 0:
            return 0.0, 0.0, 0.0

        return (
            float(np.mean(self.pitch)),
            float(np.mean(self.yaw)),
            float(np.mean(self.roll))
        )