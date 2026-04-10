import cv2
import time
import tkinter as tk
from tkinter import ttk, messagebox
import config

from detector import FaceDetector
from headpose import HeadPoseEstimator
from smoother import Smoother
from classifier import BehaviorClassifier
from logger import Logger


BUTTONS = {}
is_running = False
should_quit = False


def build_start_form():
    result = {
        "host_name": None,
        "studio_id": None,
        "location": None,
        "submitted": False
    }

    root = tk.Tk()
    root.title("ORCA - Start Session")
    root.geometry("450x800")
    root.minsize(450, 800)
    root.maxsize(450, 800)
    root.resizable(False, False)
    root.configure(bg="#EAF4FF")

    def center_window(window, width=450, height=800):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    center_window(root)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Modern.TCombobox",
        fieldbackground="#FFFFFF",
        background="#FFFFFF",
        foreground="#0F172A",
        bordercolor="#BFDBFE",
        lightcolor="#BFDBFE",
        darkcolor="#BFDBFE",
        arrowcolor="#60A5FA",
        relief="flat",
        padding=10,
        font=("Segoe UI", 12)
    )

    def only_number(value):
        return value.isdigit() or value == ""

    vcmd = (root.register(only_number), "%P")

    def create_labeled_entry(parent, label_text, default_value="", numbers_only=False):
        wrapper = tk.Frame(parent, bg="#FFFFFF")
        wrapper.pack(fill="x", pady=(0, 18))

        label = tk.Label(
            wrapper,
            text=label_text,
            bg="#FFFFFF",
            fg="#334155",
            font=("Segoe UI", 10, "bold")
        )
        label.pack(anchor="w", pady=(0, 8))

        outer_field = tk.Frame(wrapper, bg="#BFDBFE", bd=0, highlightthickness=0)
        outer_field.pack(fill="x")

        entry = tk.Entry(
            outer_field,
            bg="#FFFFFF",
            fg="#0F172A",
            insertbackground="#0F172A",
            relief="flat",
            bd=0,
            font=("Segoe UI", 12)
        )

        if numbers_only:
            entry.configure(validate="key", validatecommand=vcmd)

        entry.pack(fill="x", padx=1, pady=1, ipady=14)
        entry.insert(0, default_value)
        return entry

    def create_labeled_dropdown(parent, label_text, values):
        wrapper = tk.Frame(parent, bg="#FFFFFF")
        wrapper.pack(fill="x", pady=(0, 18))

        label = tk.Label(
            wrapper,
            text=label_text,
            bg="#FFFFFF",
            fg="#334155",
            font=("Segoe UI", 10, "bold")
        )
        label.pack(anchor="w", pady=(0, 8))

        selected = tk.StringVar()
        combo = ttk.Combobox(
            wrapper,
            textvariable=selected,
            values=values,
            state="readonly",
            style="Modern.TCombobox",
            font=("Segoe UI", 12)
        )
        combo.pack(fill="x", ipady=8)
        combo.set(values[0])

        return selected

    outer = tk.Frame(root, bg="#EAF4FF")
    outer.pack(fill="both", expand=True, padx=18, pady=18)

    card = tk.Frame(
        outer,
        bg="#FFFFFF",
        bd=0,
        highlightthickness=1,
        highlightbackground="#DBEAFE"
    )
    card.pack(fill="both", expand=True)

    header = tk.Frame(card, bg="#FFFFFF")
    header.pack(fill="x", padx=28, pady=(30, 8))

    badge = tk.Label(
        header,
        text="ORCA",
        bg="#DBEAFE",
        fg="#2563EB",
        font=("Segoe UI", 9, "bold"),
        padx=12,
        pady=6
    )
    badge.pack(anchor="w", pady=(0, 14))

    title = tk.Label(
        header,
        text="Start Monitoring Session",
        bg="#FFFFFF",
        fg="#0F172A",
        font=("Segoe UI", 22, "bold")
    )
    title.pack(anchor="w")

    subtitle = tk.Label(
        header,
        text="Isi data host dan studio sebelum monitoring dimulai",
        bg="#FFFFFF",
        fg="#64748B",
        font=("Segoe UI", 10)
    )
    subtitle.pack(anchor="w", pady=(8, 0))

    divider = tk.Frame(card, bg="#EFF6FF", height=1)
    divider.pack(fill="x", padx=28, pady=(18, 22))

    form = tk.Frame(card, bg="#FFFFFF")
    form.pack(fill="x", padx=28)

    host_entry = create_labeled_entry(form, "Host Name", "")
    studio_entry = create_labeled_entry(form, "Studio Number", "", numbers_only=True)
    location_var = create_labeled_dropdown(form, "Tempat", ["Jakarta", "Bandung"])

    info_box = tk.Frame(card, bg="#F8FBFF", highlightthickness=1, highlightbackground="#DBEAFE")
    info_box.pack(fill="x", padx=28, pady=(6, 0))

    info_label = tk.Label(
        info_box,
        text="Studio Number hanya boleh angka. Tempat dipilih sesuai cabang operasional.",
        bg="#F8FBFF",
        fg="#64748B",
        font=("Segoe UI", 9),
        justify="left",
        wraplength=330
    )
    info_label.pack(anchor="w", padx=14, pady=12)

    spacer = tk.Frame(card, bg="#FFFFFF")
    spacer.pack(fill="both", expand=True)

    error_label = tk.Label(
        card,
        text="",
        bg="#FFFFFF",
        fg="#DC2626",
        font=("Segoe UI", 9, "bold")
    )
    error_label.pack(anchor="w", padx=28, pady=(8, 10))

    button_frame = tk.Frame(card, bg="#FFFFFF")
    button_frame.pack(fill="x", padx=28, pady=(0, 28), side="bottom")

    def confirm():
        host_name = host_entry.get().strip()
        studio_number = studio_entry.get().strip()
        location = location_var.get().strip()

        if not host_name:
            error_label.config(text="Host Name wajib diisi.")
            return

        if not studio_number:
            error_label.config(text="Studio Number wajib diisi.")
            return

        if not location:
            error_label.config(text="Tempat wajib dipilih.")
            return

        try:
            studio_id = f"S{int(studio_number):02d}"
        except ValueError:
            error_label.config(text="Studio Number harus angka.")
            return

        result["host_name"] = host_name
        result["studio_id"] = studio_id
        result["location"] = location
        result["submitted"] = True
        root.destroy()

    def cancel():
        root.destroy()

    confirm_btn = tk.Button(
        button_frame,
        text="Confirm",
        command=confirm,
        bg="#60A5FA",
        fg="white",
        activebackground="#3B82F6",
        activeforeground="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 13, "bold"),
        cursor="hand2",
        height=2
    )
    confirm_btn.pack(fill="x", pady=(0, 12))

    cancel_btn = tk.Button(
        button_frame,
        text="Cancel",
        command=cancel,
        bg="#EFF6FF",
        fg="#2563EB",
        activebackground="#DBEAFE",
        activeforeground="#1D4ED8",
        relief="flat",
        bd=0,
        font=("Segoe UI", 12, "bold"),
        cursor="hand2",
        height=2
    )
    cancel_btn.pack(fill="x")

    root.bind("<Return>", lambda event: confirm())
    root.mainloop()
    return result


def draw_card(frame, x1, y1, x2, y2, fill=(250, 252, 255), border=(225, 232, 240)):
    cv2.rectangle(frame, (x1, y1), (x2, y2), fill, -1)
    cv2.rectangle(frame, (x1, y1), (x2, y2), border, 1)


def draw_text(frame, text, x, y, scale=0.5, color=(40, 40, 40), thickness=1):
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA
    )


def draw_badge(frame, text, x, y, fill, text_color, scale=0.43):
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)[0]
    pad_x = 10
    pad_y = 7
    x2 = x + text_size[0] + pad_x * 2
    y2 = y + text_size[1] + pad_y * 2
    cv2.rectangle(frame, (x, y), (x2, y2), fill, -1)
    draw_text(frame, text, x + pad_x, y + pad_y + text_size[1], scale, text_color, 1)
    return x2, y2


def draw_info_row(frame, label, value, x, y):
    draw_text(frame, label, x, y, 0.48, (120, 130, 145), 1)
    draw_text(frame, value, x + 78, y, 0.50, (35, 35, 35), 1)


def draw_clean_button(frame, name, x1, y1, x2, y2, label, fill, border, text_color):
    BUTTONS[name] = (x1, y1, x2, y2)
    cv2.rectangle(frame, (x1, y1), (x2, y2), fill, -1)
    cv2.rectangle(frame, (x1, y1), (x2, y2), border, 1)

    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)[0]
    tx = x1 + ((x2 - x1) - text_size[0]) // 2
    ty = y1 + ((y2 - y1) + text_size[1]) // 2
    draw_text(frame, label, tx, ty, 0.52, text_color, 1)


def mouse_callback(event, x, y, flags, param):
    global is_running, should_quit

    if event != cv2.EVENT_LBUTTONDOWN:
        return

    for name, (x1, y1, x2, y2) in BUTTONS.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            if name == "start":
                is_running = True
            elif name == "pause":
                is_running = False
            elif name == "quit":
                should_quit = True
            break


session_info = build_start_form()

if not session_info["submitted"]:
    print("Session dibatalkan.")
    raise SystemExit

HOST_NAME = session_info["host_name"]
STUDIO_ID = session_info["studio_id"]
LOCATION = session_info["location"]

cap = cv2.VideoCapture(config.CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1280)

if not cap.isOpened():
    messagebox.showerror("Camera Error", "Kamera default tidak bisa dibuka. Cek config.CAMERA_INDEX.")
    raise SystemExit

detector = FaceDetector()
pose = HeadPoseEstimator()
smooth = Smoother(config.SMOOTH_WINDOW)
clf = BehaviorClassifier(config)

logger = Logger(
    studio_id=STUDIO_ID,
    host_name=HOST_NAME,
    location=LOCATION
)

frame_count = 0
last_log_time = 0
last_status = "idle"

window_name = "ORCA Monitoring"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setMouseCallback(window_name, mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    status = last_status

    if is_running:
        if frame_count % config.PROCESS_EVERY_N_FRAMES == 0:
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
            last_status = status

            now = time.time()
            if now - last_log_time >= 1:
                logger.log(face, pitch, yaw, roll, status)
                last_log_time = now

    h, w = frame.shape[:2]

    card_x1 = 20
    card_y1 = 20
    card_x2 = min(w - 20, 430)
    card_y2 = 170

    draw_card(frame, card_x1, card_y1, card_x2, card_y2)
    draw_text(frame, "ORCA MONITOR", 34, 48, 0.62, (45, 95, 180), 1)

    if is_running:
        system_fill = (232, 245, 234)
        system_text = (46, 125, 50)
        system_label = "RUNNING"
    else:
        system_fill = (245, 247, 250)
        system_text = (100, 116, 139)
        system_label = "PAUSED"

    status_map = {
        "facing_camera": ((227, 242, 253), (30, 100, 190), "Facing"),
        "head_down": ((255, 243, 224), (180, 120, 20), "Head Down"),
        "not_facing_camera": ((255, 248, 225), (160, 120, 20), "Not Facing"),
        "off_frame": ((255, 235, 238), (198, 40, 40), "Off Frame"),
        "idle": ((245, 247, 250), (120, 130, 145), "Idle"),
    }

    badge_fill, badge_text, badge_label = status_map.get(
        status, ((245, 247, 250), (120, 130, 145), status)
    )

    draw_badge(frame, f"System: {system_label}", 34, 62, system_fill, system_text, 0.43)
    draw_badge(frame, f"Status: {badge_label}", 180, 62, badge_fill, badge_text, 0.43)

    draw_info_row(frame, "Host", HOST_NAME, 34, 112)
    draw_info_row(frame, "Studio", STUDIO_ID, 34, 140)
    draw_info_row(frame, "Tempat", LOCATION, 220, 112)

    action_x1 = 20
    action_y1 = 180 
    action_x2 = min(w - 20, 430)
    action_y2 = 240

    draw_card(frame, action_x1, action_y1, action_x2, action_y2)

    btn_y1 = action_y1 + 12
    btn_y2 = action_y2 - 12
    btn_w = 108
    gap = 10
    start_x = 34

    draw_clean_button(
        frame, "start",
        start_x, btn_y1, start_x + btn_w, btn_y2,
        "Start",
        (239, 246, 255),
        (191, 219, 254),
        (37, 99, 235)
    )

    draw_clean_button(
        frame, "pause",
        start_x + btn_w + gap, btn_y1, start_x + (btn_w * 2) + gap, btn_y2,
        "Pause",
        (248, 250, 252),
        (226, 232, 240),
        (71, 85, 105)
    )

    draw_clean_button(
        frame, "quit",
        start_x + (btn_w * 2) + (gap * 2), btn_y1, start_x + (btn_w * 3) + (gap * 2), btn_y2,
        "Quit",
        (254, 242, 242),
        (254, 202, 202),
        (220, 38, 38)
    )

    cv2.imshow(window_name, frame)

    if should_quit:
        break

    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

    cv2.waitKey(1)

cap.release()
logger.close()
cv2.destroyAllWindows()