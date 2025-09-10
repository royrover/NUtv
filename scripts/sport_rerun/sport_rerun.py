import os
import json
from datetime import datetime

# บังคับใช้ folder จาก root ของ repo
SAVE_DIR = os.path.join(os.getcwd(), "data", "sport_rerun")
os.makedirs(SAVE_DIR, exist_ok=True)

json_file = os.path.join(SAVE_DIR, "sport_rerun.json")

data = {
    "name": "Sport Replay",
    "author": "royrover",
    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "groups": [
        {
            "name": f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "url": "",
            "import": False
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
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("✅ File created:", json_file)
except Exception as e:
    print("❌ Failed to create file:", e)

# ตรวจสอบ folder contents
print("Listing folder contents after write:")
print(os.listdir(SAVE_DIR))
