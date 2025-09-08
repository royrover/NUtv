import requests
import json
from datetime import datetime
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
json_file = os.path.join(SAVE_DIR, "goaldaddyth.json")

def response_status_code(response):
    if response.status_code == 200:
        print("✅ เชื่อมต่อสำเร็จ:", response.url if hasattr(response, 'url') else 'URL ไม่ระบุ')
        print("Status Code:", response.status_code)
    else:
        print("❌ เชื่อมต่อไม่สำเร็จ:", response.url if hasattr(response, 'url') else 'URL ไม่ระบุ')
        print("Status Code:", response.status_code)

# Header เริ่มต้นใช้ login
headers_1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Referer": "https://www.goaldaddyth.com/",
    "Origin": "https://www.goaldaddyth.com",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
    "Content-Type": "application/json; charset=utf-8"
}

# เริ่ม login เพื่อรับ token
url = 'https://api.gdaddy.tv/v3/user/guest/login'
payload = {"guid": "9c1e7610-4db5-44c9-8753-3f6a13edfb63"}

response = requests.post(url, headers=headers_1, data=json.dumps(payload))
response_status_code(response)
response.encoding = 'utf-8'

try:
    json_data = response.json()
except Exception as e:
    print("❌ ไม่สามารถแปลง JSON ได้:", e)
    exit()

token = json_data['data']['token']

# Header สำหรับเข้าถึง API จริง
headers_2 = headers_1.copy()
headers_2["Authorization"] = f"Bearer {token}"


# โหลดไฟล์เดิมถ้ามี
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "name": "Sports Replays",
        "image": "https://www.goaldaddyth.com/logos/goaldaddy-logo.webp",
        "url": "",
        "author": "",
        "stations": []
    }

stations_list = data["stations"]
existing_urls = set(item["url"] for item in stations_list)
new_stations = []

# ดึงข้อมูลจากหลายหน้า
start_page = 1
end_page = 1

for page in range(start_page, end_page + 1):
    api_url = f"https://api.gdaddy.tv/v1/liveStream/playback?languageId=3&pageNumber={page}&rowCount=12&sportIds=0&sportIds=1"
    print(f"📦 ดึงข้อมูลจากหน้า {page}: {api_url}")
    
    try:
        response = requests.get(api_url, headers=headers_2)
        response_status_code(response)
        response.encoding = 'utf-8'

        json_data = response.json()
        all_data = json_data.get('data', {}).get('liveStreamsPlayback', [])

        for item in all_data:
            final_url = item.get('streamUrl')
            title = item.get('streamTitle')
            image = item.get('streamThumbnailUrl')
            if 'vodthumbnails' in image:
                image = "https://media.gq.com/photos/59e76aaaf964810d9a9b8d2f/16:9/w_1600,c_limit/GQ_50Greatest_final_v2.jpg"
            else:
                image = image

            if not final_url or final_url in existing_urls:
                print("⏩ ข้าม (ลิงก์ซ้ำหรือว่าง)")
                continue

            station_data = {
                "name": title,
                "image": image,
                "url": final_url,
                "referer": headers_1['Referer'],
                "userAgent": headers_1['User-Agent']
            }

            new_stations.append(station_data)
            existing_urls.add(final_url)
            print(f"✅ เพิ่ม: {title}")

    except requests.RequestException as e:
        print(f"❌ Error fetching page {page}: {e}")
        continue
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error on page {page}: {e}")
        continue

# ✅ อัปเดตข้อมูล
data["stations"] = new_stations + stations_list
data["author"] = f"update {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"

# ✅ เขียนไฟล์ JSON (.w3u)
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(json.dumps(data, ensure_ascii=False, indent=4))
print(f"✅ File {output_file} updated successfully.")

data['author'] = f"update {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"

# ✅ สร้างไฟล์ .m3u
m3u_content = "#EXTM3U\n"
ref = "|User-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/605.1.15/Clipbox+/2.2.8&Referer=https://dooball.id/"

for station in data["stations"]:
    m3u_content += f'#EXTINF:-1 tvg-logo="{station["image"]}" group-title="Sports Replays", {station["name"]}\n{station["url"]}{ref}\n'

with open(m3u_file, "w", encoding="utf-8") as f:
    print(m3u_content)
    f.write(m3u_content)

print("✅ บันทึกเรียบร้อย:", json_file, "และ", m3u_file)
