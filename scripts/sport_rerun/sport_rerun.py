import json
import os
import platform
from datetime import datetime

# === ตรวจสอบระบบปฏิบัติการ ===
SYSTEM = platform.system()
if SYSTEM == "Windows":
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
elif SYSTEM == "Linux":
    SAVE_DIR = os.path.join(os.getcwd(), "data/sport_rerun")
else:  # Android (Termux)
    SAVE_DIR = "/storage/emulated/0/htdocs/PYTHON/live_sport"
    
os.makedirs(SAVE_DIR, exist_ok=True)
json_file = os.path.join(SAVE_DIR, "sport_rerun.m3u")

data = {
    "name": "Sport Replay",
    "author": "royrover",
    "image": "https://www.dropbox.com/scl/fi/580b56xuardpwn9ufybox/sports-replays.png?rlkey=k806o9d2aqlfytgvhbrnbteuj&st=3wauyveb&raw=1",
    "url": "",
    "groups": [
        {
            "name": f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "image": "https://i.pinimg.com/originals/2c/64/60/2c6460852e1c2a13a3e7ac8bea39acd3.gif",
            "url": "",
            "import": False,
        },
{
            "name": "goaldaddyth",
            "image": "https://i1.sndcdn.com/avatars-sen5MqKQrKyo43a7-2M6hlg-t1080x1080.jpg",
            "url": "",
            "import": False
        },
        {
            "name": "acdsport",
            "image": "https://i1.sndcdn.com/avatars-sen5MqKQrKyo43a7-2M6hlg-t1080x1080.jpg",
            "url": "",
            "import": False
        },
        {
            "name": "dookeela",
            "image": "https://i1.sndcdn.com/avatars-sen5MqKQrKyo43a7-2M6hlg-t1080x1080.jpg",
            "url": "",
            "import": False
        }
    ]
}

with open(json_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)
print(json.dumps(data, indent=4, ensure_ascii=False))

print(f"✅ อัปเดตไฟล์เรียบร้อย: {json_file}")
