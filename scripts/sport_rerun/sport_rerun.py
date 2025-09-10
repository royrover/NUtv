import json
import os
import platform
from datetime import datetime
from zoneinfo import ZoneInfo  # สำหรับตั้ง timezone

# === ตรวจสอบระบบปฏิบัติการ ===
SYSTEM = platform.system()
if SYSTEM == "Windows":
    SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/sport_rerun")
elif SYSTEM == "Linux":
    SAVE_DIR = os.path.join(os.getcwd(), "data/sport_rerun")
else:  # Android (Termux)
    SAVE_DIR = "/storage/emulated/0/htdocs/PYTHON/live_sport"

# สร้างโฟลเดอร์ถ้ายังไม่มี
os.makedirs(SAVE_DIR, exist_ok=True)

# ตั้งชื่อไฟล์ (ให้เป็น .json)
json_file = os.path.join(SAVE_DIR, "sport_rerun.json")

# เวลาไทย
now_th = datetime.now(ZoneInfo("Asia/Bangkok"))

# ข้อมูลตัวอย่าง
data = {
    "name": "Sport Replay",
    "author": "royrover",
    "image": "https://www.dropbox.com/scl/fi/580b56xuardpwn9ufybox/sports-replays.png?rlkey=k806o9d2aqlfytgvhbrnbteuj&st=3wauyveb&raw=1",
    "url": "",
    "groups": [
        {
            "name": f"Update {now_th.strftime('%Y-%m-%d %H:%M:%S')}",  # เวลาไทยตรง ๆ
            "image": "https://i.pinimg.com/originals/2c/64/60/2c6460852e1c2a13a3e7ac8bea39acd3.gif",
            "url": "",
            "import": False,
        },
        {
            "name": "acdsport",
            "image": "https://i1.sndcdn.com/avatars-sen5MqKQrKyo43a7-2M6hlg-t1080x1080.jpg",
            "url": "https://raw.githubusercontent.com/royrover/NUtv/main/data/sport_rerun/acdsport_replay.json",
            "import": False
        },
        {
            "name": "dookeela",
            "image": "https://i1.sndcdn.com/avatars-sen5MqKQrKyo43a7-2M6hlg-t1080x1080.jpg",
            "url": "https://raw.githubusercontent.com/royrover/NUtv/main/data/sport_rerun/dookeela_rerun.json",
            "import": False
        },
        {
            "name": "goaldaddyth",
            "image": "https://i1.sndcdn.com/avatars-sen5MqKQrKyo43a7-2M6hlg-t1080x1080.jpg",
            "url": "https://raw.githubusercontent.com/royrover/NUtv/main/data/sport_rerun/goaldaddyth.json",
            "import": False
        }
    ]
}

# === เขียนไฟล์ JSON ===
with open(json_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print(f"✅ อัปเดตไฟล์เรียบร้อย: {json_file}")
