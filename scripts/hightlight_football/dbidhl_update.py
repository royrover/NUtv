import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import os
import platform

# === ตรวจสอบระบบปฏิบัติการ ===
SYSTEM = platform.system()

SYSTEM = platform.system()

if SYSTEM == "Windows":
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
elif SYSTEM == "Linux":
    SAVE_DIR = os.path.join(os.getcwd(), "data/highlight_football")
else:  # Android (Termux)
    SAVE_DIR = "/storage/emulated/0/htdocs/PYTHON/HL UPDATE/Highlight Football"

os.makedirs(SAVE_DIR, exist_ok=True)
json_file = os.path.join(SAVE_DIR, "dbidhl.json")


if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        'name': 'highlights - dooball_id',
        'image': 'https://dooball.id/images/logo/rBdVFRtw3Qf9WtZz9P6yfNaZXEUywKGlogo_2.png',
        'url': 'https://dl.dropbox.com/scl/fi/hw8el5fsspkyqgtt23qvd/dbidhl.w3u?rlkey=vl74squo3v3jqtqnkwq9jfulb&st=8kdsstzs&dl=0',
        'author': "",
        'stations': []
    }

stations_list = data["stations"]
existing_urls = set(item["url"] for item in stations_list)
new_stations = []

base_url = "https://dooball.id/highlights"
start_page = 1
end_page = 5

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://dooball.id/"
}

for page in range(start_page, end_page + 1):
    url = f"{base_url}?page={page}"
    print(f"🔎 Fetching URL: {url}\n")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        highlights = soup.find_all('div', {'class': 'card shadow w-100'})

        for highlight in highlights:
            title_tag = highlight.find('h2', {'class': 'fs-5'})
            img_tag = highlight.find('img')
            link_tag = highlight.find('a', {'class': 'stretched-link'})

            title = title_tag.text.strip() if title_tag else "N/A"
            title = title.replace("#ไฮไลท์ฟุตบอล ", "").replace("[", "").replace(']', '-')
            image = img_tag['src'] if img_tag else "N/A"
            if image and not image.startswith("http"):
                image = "https://dooball.id" + image
            link = link_tag['href'] if link_tag else "N/A"
            if link and not link.startswith("http"):
                link = "https://dooball.id" + link

            try:
                raw_html = requests.get(link, headers=headers, timeout=10)
                raw_html.raise_for_status()
                soup = BeautifulSoup(raw_html.text, 'html.parser')

                video_tag = soup.find('div', class_='embed-responsive embed-responsive-16by9')

                final_url = "N/A"
                if video_tag:
                    iframe = video_tag.find('iframe')
                    if iframe:
                        iframe_src = iframe['src']
                        if iframe_src.startswith("http"):
                            try:
                                iframe_response = requests.get(iframe_src, headers=headers, timeout=10)
                                soup = BeautifulSoup(iframe_response.text, 'html.parser')

                                script_tag = soup.find('script', string=re.compile(r"var url ="))

                                if script_tag:
                                    match = re.search(r"var url = '(https?://[^']+\.m3u8)'", script_tag.string)
                                    if match:
                                        final_url = match.group(1)
                                    else:
                                        print("m3u8 link not found in script.")
                                else:
                                    print("Script tag containing m3u8 link not found.")

                                print(f"🔎 Highlight title: {title}\n 📺 url link: {final_url}")
                            except requests.RequestException as e:
                                print(f"❌ Error fetching iframe for {title}: {e}")
                                continue

                if not final_url or final_url in existing_urls:
                    print("⏩ ข้าม (ลิงก์ซ้ำหรือว่าง)")
                    continue

                station_data = {
                    'name': f"⚽ {title}",
                    'image': image,
                    'url': final_url,
                    'referer': 'https://dooball.id/',
                    'userAgent': headers['User-Agent'],
                    'playInNatPlayer': 'true'
                }
                new_stations.append(station_data)
                existing_urls.add(final_url)
                print(f"✅ เพิ่ม: {title}")

            except requests.RequestException as e:
                print(f"❌ Error fetching video for {title}: {e}")
                continue

    except requests.RequestException as e:
        print(f"❌ Error fetching page {page}: {e}")
        continue

# ✅ อัปเดตข้อมูล
data["stations"] = new_stations + stations_list
data["author"] = f"update {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"

# ✅ เขียนไฟล์ JSON (.w3u)
with open(json_file, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(json.dumps(data, ensure_ascii=False, indent=4))
print(f"✅ File {json_file} updated successfully.")


