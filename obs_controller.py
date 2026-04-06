from obswebsocket import obsws, requests
import time

class OBSController:
    def __init__(self, host="localhost", port=4455, password="BfdOwxizVRPN8pxx"):
        self.ws = obsws(host, port, password)
        self.ws.connect()
        self.is_streaming = False

    def check_stream(self):
        status = self.ws.call(requests.GetStreamStatus())
        return status.getOutputActive()

    def wait_for_stream_start(self):
        print("⏳ Menunggu OBS mulai streaming...")
        while True:
            if self.check_stream():
                print("🔥 STREAM START DETECTED")
                self.is_streaming = True
                return
            time.sleep(1)

    def wait_for_stream_stop(self):
        print("⏳ Monitoring berjalan...")
        while True:
            if not self.check_stream():
                print("🛑 STREAM STOP DETECTED")
                self.is_streaming = False
                return
            time.sleep(1)