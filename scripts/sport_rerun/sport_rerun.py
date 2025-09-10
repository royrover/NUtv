import os
import json
from datetime import datetime

# บังคับใช้ folder จาก repo root
SAVE_DIR = os.path.join(os.getcwd(), "data", "sport_rerun")
os.makedirs(SAVE_DIR, exist_ok=True)
print("SAVE_DIR:", SAVE_DIR)

json_file = os.path.join(SAVE_DIR, "sport_rerun.json")  # ใช้ .json test ก่อน
print("Will save JSON to:", json_file)

# ตัวอย่างข้อมูล
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
        },
        {
            "name": "dookeela",
            "url": "https://raw.githubusercontent.com/royrover/NUtv/refs/heads/main/data/sport_rerun/dookeela_rerun.json",
            "import": False
        },
        {
            "name": "goaldaddyth",
            "url": "https://raw.githubusercontent.com/royrover/NUtv/refs/heads/main/data/sport_rerun/goaldaddyth.json",
            "import": False
        }
    ]
}

# เขียนไฟล์
try:
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("✅ File saved successfully:", json_file)
except Exception as e:
    print("❌ Failed to save file:", e)

# ตรวจสอบ folder
print("Listing folder contents:")
print(os.listdir(SAVE_DIR))
