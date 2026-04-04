import time
from datetime import datetime

def get_unix_timestamp():
    return int(time.time())

def get_unix_ms():
    return int(time.time() * 1000)

def get_formatted_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_iso_time():
    return datetime.utcnow().isoformat()

def get_duration(start_time):
    return time.time() - start_time

def seconds_to_hms(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"