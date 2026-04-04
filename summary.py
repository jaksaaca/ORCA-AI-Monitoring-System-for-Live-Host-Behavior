import pandas as pd

def generate_summary(file):
    df = pd.read_csv(file)

    total = len(df)

    face_presence = df["face_detected"].mean() * 100
    facing = (df["status"] == "facing_camera").mean() * 100

    head_down_duration = (df["status"] == "head_down").sum()
    off_frame_duration = (df["status"] == "off_frame").sum()

    longest_streak = (df["status"] == "head_down").astype(int)\
        .groupby((df["status"] != "head_down").cumsum())\
        .sum().max()

    print("=== SUMMARY ===")
    print("Total:", total, "seconds")
    print("Face %:", face_presence)
    print("Facing %:", facing)
    print("Head Down:", head_down_duration)
    print("Longest Head Down:", longest_streak)
    print("Off Frame:", off_frame_duration)