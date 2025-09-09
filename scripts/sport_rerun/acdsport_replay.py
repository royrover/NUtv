import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
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
json_file = os.path.join(SAVE_DIR, "acdsport_replay.json")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/237.84.2.178 Safari/537.36",
}

url = "https://acdsport.com/replay.html"

# โหลดข้อมูลเก่า ถ้ามี
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "name": "acdsport replay",
        "image": "https://acdsport.com/acd/social.jpg",
        "url": "",
        "author": "",
        "stations": [],
    }

# เก็บรายการ URL ที่มีอยู่แล้ว เพื่อป้องกันข้อมูลซ้ำ
existing_urls = set(item["url"] for item in data["stations"])

# เก็บ URL ตัวแรกของรอบก่อน (ใช้ตรวจซ้ำแล้ว break)
old_first_url = data["stations"][0]["url"] if data["stations"] else None

new_stations = []
stop_fetch = False

response = requests.get(url, headers=headers)
response.encoding = "utf-8"
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
all_links = soup.find_all(
    "div", class_="d-flex justify-content-between fixture-page-item active"
)

for link in all_links:
    if stop_fetch:
        break
    try:
        time = link.find("p", class_="time-format").text.strip()
        league = link.find("div", class_="mt-1 tournament").text.strip()
        home_team = link.find("span", class_="name-team name-team-left").text.strip()
        home_img = (
            link.find_all("img", class_="logo-team")[0]["src"]
            if link.find_all("img", class_="logo-team")
            else None
        )
        away_team = link.find("span", class_="name-team name-team-right").text.strip()
        url_link = link.find("div", class_="box-play").a["href"]
        if not url_link:
            continue

        full_url = url_link
        print(f"⚽ {time} {league} {home_team} vs {away_team}")
        print(f"🌐 กำลังดึง: {full_url}")

        response_match = requests.get(full_url, headers=headers)
        response_match.raise_for_status()
        match_html = response_match.text

        match_soup = BeautifulSoup(match_html, "html.parser")
        iframe_src = match_soup.find("iframe", id="iframePlayer").get("src")
        iframe_response = requests.get(iframe_src, headers=headers)
        iframe_response.raise_for_status()
        iframe_html = iframe_response.text

        final_url_match = re.search(r'link:"(http.*?\.m3u8)"', iframe_html)
        if final_url_match:
            final_url = final_url_match.group(1).encode().decode("unicode_escape")

            # ✅ ถ้าเจอลิงก์ตรงกับรอบก่อน → หยุดดึงข้อมูล
            if old_first_url and final_url == old_first_url:
                print("⏹️ เจอลิงก์ซ้ำกับรอบที่แล้ว หยุดดึงข้อมูล")
                stop_fetch = True
                break

            if final_url in existing_urls:
                print("⏩ ข้าม (ลิงก์ซ้ำในไฟล์ปัจจุบัน)")
                continue

            # เพิ่มรายการใหม่ไว้ด้านบน
            station_data = {
                "name": f"{time} {league} {home_team} vs {away_team}",
                "image": home_img,
                "url": final_url,
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/605.1.15/Clipbox+/2.2.8",
                "referer": "https://acdsport.com/",
            }
            new_stations.append(station_data)
            existing_urls.add(final_url)
            print(f"✅ เพิ่ม: {station_data['name']}")
        else:
            print("❌ ไม่พบลิงก์ m3u8")
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
print(json.dumps(data, ensure_ascii=False, indent=2))
print("✅ บันทึกเรียบร้อย:", json_file)
