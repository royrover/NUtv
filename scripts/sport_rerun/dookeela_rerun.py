# dookeela_rerun.py
import requests
from datetime import datetime
import json
import os
import platform

# === ตรวจสอบระบบปฏิบัติการ ===
SYSTEM = platform.system()

if SYSTEM == "Windows":
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
elif SYSTEM == "Linux":
    SAVE_DIR = os.path.join(os.getcwd(), "data/sport_rerun")
else:  # Android (Termux)
    SAVE_DIR = "/storage/emulated/0/htdocs/PYTHON/HL UPDATE /Highlight Football"

os.makedirs(SAVE_DIR, exist_ok=True)
json_file = os.path.join(SAVE_DIR, "dookeela_rerun.json")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.36.2.178 Safari/537.36",
}

# โหลดข้อมูลเก่า ถ้ามี
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "name": "DOOKEELA Rerun",
        "image": "https://www.dropbox.com/scl/fi/0wslhpbbirva0wx4rlbzn/DKL.png?rlkey=37e1vu25obzmo5kikjkax30t7&st=7ey1fj5e&raw=1",
        "url": "",
        "author": "",
        "stations": [],
    }

# เก็บ URL ที่มีอยู่แล้วกันซ้ำ
existing_urls = set(item["url"] for item in data["stations"])

new_stations = []
skip_count = 0

for page in range(1, 4):  # ✅ ดึงหน้า 1-3
    try:
        url = f"https://dookeela.live/api/reruns?page={page}"
        print(f"\n📌 ดึงข้อมูลหน้า {page}: {url}")

        response = requests.get(url, headers=headers).json()
        for item in response.get("data", []):
            final_url = item.get("video_url")
            if not final_url or final_url in existing_urls:
                print("⏩ ข้าม (ลิงก์ซ้ำหรือว่าง)")
                continue

            # 🚫 ข้าม YouTube highlight
            if "youtube.com" in final_url or "youtu.be" in final_url:
                print("⏩ ข้าม (YouTube Highlight)")
                continue

            # ✅ ใช้ title ถ้ามีค่า
            if item.get("title"):
                title = item["title"]
            else:
                fixture = item.get("fixture")
                if fixture:
                    league = fixture.get("league", {}).get("name", "Unknown League")
                    home = fixture.get("teamhome", {}).get("name", "Home")
                    away = fixture.get("teamaway", {}).get("name", "Away")
                    title = f"{home} vs {away} | {league}"
                else:
                    # fallback ถ้าไม่มี fixture + title เป็น null
                    base_name = os.path.basename(final_url).replace(".mp4/playlist.m3u8", "")
                    title = base_name.replace("%20", " ")

            new_stations.append({
                "name": title,
                "image": item.get("thumbnail_path"),
                "url": final_url
            })
            existing_urls.add(final_url)
            print(f"✅ เพิ่ม: {title}")



        if not response.get("data"):
            print("❌ ไม่พบข้อมูลในหน้านี้")
    except Exception as e:
        print(f"⚠️ Error: {e}")
        continue

# เพิ่มรายการใหม่ไว้ด้านบน
data["stations"] = new_stations + data["stations"]

# อัปเดตวันที่ล่าสุด
data["author"] = f"update {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"

# บันทึก JSON
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
print(json.dumps(data, ensure_ascii=False, indent=4))

print(f"✅ บันทึกเรียบร้อย: {json_file}")
