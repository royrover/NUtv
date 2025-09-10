import os
import json
from datetime import datetime

# ✅ ใช้ folder จาก repo root เสมอ
SAVE_DIR = os.path.join(os.getcwd(), "data", "sport_rerun")
os.makedirs(SAVE_DIR, exist_ok=True)

# ไฟล์ JSON/M3U
json_file = os.path.join(SAVE_DIR, "sport_rerun.json")  # สำหรับ test ใช้ .json

# ข้อมูลตัวอย่าง
data = {
    "name": "Sport Replay",
    "author": "royrover",
    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "groups": [
        {
            "name": f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "url": "",
            "import": False,
        },
        {
            "name": "acdsport",
            "url": "https://raw.githubusercontent.com/royrover/NUtv/refs/heads/main/data/sport_rerun/acdsport_replay.json",
            "import": False
        }
    ]
}

# เขียนไฟล์พร้อม debug
try:
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("✅ File saved successfully:", json_file)
except Exception as e:
    print("❌ Failed to save file:", e)

# แสดงไฟล์ใน folder
print("Listing folder contents:")
print(os.listdir(SAVE_DIR))
