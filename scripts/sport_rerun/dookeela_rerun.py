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
    SAVE_DIR = "/storage/emulated/0/htdocs/PYTHON/HL UPDATE/sport_rerun"

os.makedirs(SAVE_DIR, exist_ok=True)
json_file = os.path.join(SAVE_DIR, "dookeela_rerun.json")
m3u_file = os.path.join(SAVE_DIR, "dookeela_rerun.m3u")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.36.2.178 Safari/537.36",
}

# โหลดข้อมูลเก่า
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

existing_urls = set(item["url"] for item in data["stations"])
old_first_url = data["stations"][0]["url"] if data["stations"] else None

new_stations = []
stop_fetch = False

for page in range(1, 4):  # ✅ หน้า 1-3
    if stop_fetch:
        break
    try:
        url = f"https://dookeela.live/api/reruns?page={page}"
        print(f"\n📌 ดึงข้อมูลหน้า {page}: {url}")
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        response = resp.json()
    except Exception as e:
        print(f"⚠️ Error: {e}")
        continue

    for item in response.get("data", []):
        final_url = item.get("video_url")
        if not final_url:
            print("⏩ ข้าม (URL ว่าง)")
            continue

        created_date = None
        try:
            dt = datetime.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            created_date = dt.strftime("%d-%m-%Y")
        except:
            created_date = "Unknown"

        if old_first_url and final_url == old_first_url:
            print("⏹️ เจอลิงก์ซ้ำกับรอบที่แล้ว หยุดดึงข้อมูล")
            stop_fetch = True
            break

        if final_url in existing_urls:
            print("⏩ ข้าม (ลิงก์ซ้ำในไฟล์ปัจจุบัน)")
            continue

        if "youtube.com" in final_url or "youtu.be" in final_url:
            print("⏩ ข้าม (YouTube Highlight)")
            continue

        # ✅ title + วันที่
        if item.get("title"):
            title = f"{item['title']} - {created_date}"
        else:
            fixture = item.get("fixture")
            if fixture:
                league = fixture.get("league", {}).get("name", "Unknown League")
                home = fixture.get("teamhome", {}).get("name", "Home")
                away = fixture.get("teamaway", {}).get("name", "Away")
                title = f"{home} vs {away} | {league} ({created_date})"
            else:
                base_name = os.path.basename(final_url).replace(".mp4/playlist.m3u8", "")
                title = f"{base_name.replace('%20', ' ')} - {created_date}"

        new_stations.append({
            "name": title,
            "image": item.get("thumbnail_path"),
            "url": final_url
        })
        existing_urls.add(final_url)
        print(f"✅ เพิ่ม: {title}")

    if not response.get("data"):
        print("❌ ไม่พบข้อมูลในหน้านี้")

data["stations"] = new_stations + data["stations"]
data["author"] = f"update {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
data["url"] = ""

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(json.dumps(data, ensure_ascii=False, indent=4))
print(f"✅ บันทึกเรียบร้อย: {json_file}")

with open(m3u_file, "w", encoding="utf-8") as f:
    m3u_content = "#EXTM3U\n"
    for station in data["stations"]:
        image = station.get("image", "")
        name = station.get("name", "No Title").replace(":", "")
        url = station.get("url")
        m3u_content += f'#EXTINF:-1 tvg-logo="{image}", group-title="LIVE SPORT", {name}\n'
        m3u_content += f'{url}\n'
    f.write(m3u_content)
print(m3u_content)
print(f"✅ อัปเดตไฟล์ JSON และ M3U เรียบร้อย")
