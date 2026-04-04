from collections import deque
import numpy as np

class Smoother:
    def __init__(self, window=10):
        self.pitch = deque(maxlen=window)
        self.yaw = deque(maxlen=window)
        self.roll = deque(maxlen=window)

    def update(self, p, y, r):
        self.pitch.append(p)
        self.yaw.append(y)
        self.roll.append(r)

    def get(self):
        return (
            np.mean(self.pitch),
            np.mean(self.yaw),
            np.mean(self.roll)
        )