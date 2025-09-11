
import requests
from bs4 import BeautifulSoup
import json
import os
import platform
from datetime import datetime
from zoneinfo import ZoneInfo  # สำหรับตั้ง timezone

# === ตรวจสอบระบบปฏิบัติการ ===
SYSTEM = platform.system()

if SYSTEM == "Windows":
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
elif SYSTEM == "Linux":
    SAVE_DIR = os.path.join(os.getcwd(), "data/highlight_football")
else:  # Android (Termux)
    SAVE_DIR = "/storage/emulated/0/htdocs/PYTHON/HL UPDATE/Highlight Football"

os.makedirs(SAVE_DIR, exist_ok=True)
json_file = os.path.join(SAVE_DIR, "hugballhl.json")
m3u_file = os.path.join(SAVE_DIR, "hugballhl.m3u")

# เวลาไทย
today_date = datetime.now(ZoneInfo("Asia/Bangkok")).strftime("%Y-%m-%d")

def fetch_video_data(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        print(f"⚠️ Error fetching {url}: {e}")
    return None


def extract_video_url(final_html):
    try:
        soup = BeautifulSoup(final_html, 'html.parser')
        source_tag = soup.find('source', type='video/mp4')
        if source_tag and 'src' in source_tag.attrs:
            video_url = source_tag['src']
            return video_url.strip()
    except Exception as e:
        print(f"⚠️ Error extracting video URL: {e}")
    return None


# โหลดข้อมูลเก่า ถ้ามี

if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "name": "Hugball Highlights",
        "image": "https://www.hugball.net/images/logo.png",
        "url": "",
        "author": "",
        "stations": []
    }

stations_list = data["stations"]
existing_urls = set(item["url"] for item in stations_list)
new_stations = []


def main():
    base_url = "https://www.hugball.net/ajax_content_clip_all.php"
    start_page = 1
    end_page = 2

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.hugball.net/"
    }

    for page in range(start_page, end_page + 1):
        page_url = base_url if page == 1 else f"{base_url}?page={page}"
        print(f"🔎 Fetching URL: {page_url}")

        response = requests.get(page_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to retrieve {page_url}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        highlights = soup.find_all('li', class_="col-md-4 col-sm-6 col-xs-8")

        if not highlights:
            print(f"ไม่พบคลิปในหน้าที่ {page_url}")
        else:
            for highlight in highlights:
                try:
                    title = highlight.find('h3', class_='title_clip').text.strip()
                except AttributeError:
                    title = "ไม่ระบุชื่อ"

                try:
                    image = highlight.find('img')['src']
                except (AttributeError, KeyError):
                    image = None

                try:
                    links = highlight.find_all('a', target="_blank")
                    if len(links) > 1:
                        raw_url = links[1]['href']
                    else:
                        continue
                except (AttributeError, KeyError):
                    continue

                raw_url = 'https://www.hugball.net' + raw_url
                print("Title:", title)
                print("Image URL:", image)

                final_html = fetch_video_data(raw_url, headers)

                if final_html:
                    video_url = extract_video_url(final_html)
                    print("🎬 Video URL:", video_url)
                else:
                    video_url = None

                if not video_url:
                    print("⏩ ข้าม (ไม่มีลิงก์วิดีโอ)")
                    continue

                if video_url in existing_urls:
                    print("⏩ เจอลิงก์ซ้ำ หยุดการทำงานทันที")
                    return  # <<< หยุด main() เลย

                station_data = {
                    "name": "⚽ " + title,
                    "image": image,
                    "url": video_url,
                    "referer": "https://www.hugball.net/"
                }
                new_stations.append(station_data)
                existing_urls.add(video_url)
                print(f"✅ เพิ่ม: {title}")


main()

# อัปเดตข้อมูล
if new_stations:
    print(f"🆕 เพิ่มรายการใหม่ {len(new_stations)} รายการ")
    data["stations"] = new_stations + stations_list

data["author"] = f"update {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"

# เขียนไฟล์
with open(json_file, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
    
    
with open(m3u_file, 'w', encoding='utf-8') as file:
    m3u_content = "#EXTM3U\n"
    for station in data["stations"]:
        m3u_content += f'#EXTINF:-1 tvg-logo="{station["image"]}", group-title="LIVE SPORT", {station["name"].replace(":", "")}\n'
        m3u_content += f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\n'
        m3u_content += f'#EXTVLCOPT:http-referrer={station["referer"]}\n'
        m3u_content += f'{station["url"]}\n'
    file.write(m3u_content)

print(f"✅ File {json_file} และ {m3u_file} updated successfully.")







