import requests
import json
import re
import os
import platform
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

# === ตรวจสอบระบบปฏิบัติการ ===
SYSTEM = platform.system()

if SYSTEM == "Windows":
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
elif SYSTEM == "Linux":
    SAVE_DIR = os.path.join(os.getcwd(), "data/highlight_football")
else:  # Android (Termux)
    SAVE_DIR = "/storage/emulated/0/htdocs/PYTHON/HL UPDATE/Highlight Football"

os.makedirs(SAVE_DIR, exist_ok=True)
json_file = os.path.join(SAVE_DIR, "buaksibhl.json")
m3u_file = os.path.join(SAVE_DIR, "buaksibhl.m3u")

url = 'https://www.buaksib.com/football-highlights/'
headers1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
    "referer": url
}

response = requests.get(url, headers=headers1)

def fetch_video_links(video_url):
    try:
        response = requests.get(video_url, timeout=10)
        response.raise_for_status()
        match = re.search(r'"reserveEmbed3":"(https://.*?)"', response.text)
        if match:
            return match.group(1)
        else:
            print(f"⚠️ ไม่พบลิงก์วิดีโอใน {video_url}")
            return None
    except requests.RequestException as e:
        print(f"❌ เกิดข้อผิดพลาด: {e} ที่ {video_url}")
        return None


if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "name": "highlights football buaksib",
        "image": "https://www.buaksib.com/_next/image/?url=%2F_next%2Fstatic%2Fmedia%2Flogo-summer.5abd78a6.png&w=256&q=75",
        "url": "",
        "author": f"update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "stations": []
    }

stations_list = data["stations"]
existing_urls = set(item["url"] for item in stations_list)
new_stations = []
stop_flag = False  # ตัวแปรใช้หยุดเมื่อเจอลิงก์ซ้ำ

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    hl_data = soup.find('ul', {'class': 'styles_list__98Era'})
    after_match = re.search(r'"endCursor":"(.*?)"', response.text)
    after = after_match.group(1) if after_match else None

    if hl_data:
        hl_items = hl_data.find_all('li')
        for hl in hl_items:
            name_tag = hl.find('p')
            name = name_tag.text.strip() if name_tag else "Unknown"

            raw_image = f"https://www.buaksib.com{hl.find('img')['src']}" if hl.find('img') else ""
            parsed_url = urllib.parse.urlparse(raw_image)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            encoded_path = query_params.get('url', [None])[0]

            if encoded_path:
                decoded_path = urllib.parse.unquote(encoded_path).replace('api/image', 'wp-content/uploads').replace('--', '/')
                image = f"https://newbackend.buaksib.com{decoded_path}"
            else:
                image = raw_image

            raw_url = f"https://www.buaksib.com{hl.find('a')['href']}"
            final_url = fetch_video_links(raw_url)
            if not final_url:
                continue
            if final_url in existing_urls:
                print("⏩ เจอลิงก์ซ้ำ หยุดการดึงข้อมูล")
                stop_flag = True
                break

            new_stations.append({
                "name": f"⚽ {name}",
                "image": image,
                "url": final_url,
                "referer": "https://www.buaksib.com/"
            })
            existing_urls.add(final_url)
            print(f"✅ เพิ่มจากหน้าแรก: {name}")

    if not stop_flag:  # ถ้าไม่เจอลิงก์ซ้ำ จึงไปดึงต่อจาก GraphQL
        request_url = "https://newbackend.buaksib.com/graphql"
        payload = {
            "operationName": "GET_CATEGORY",
            "variables": {
                "id": "/category/football-highlights/",
                "first": 40,
                "after": after
            },
            "query": """query GET_CATEGORY($id: ID!, $first: Int, $after: String) {
              category(id: $id, idType: URI) {
                posts(first: $first, after: $after) {
                  edges {
                    node {
                      date
                      slug
                      excerpt(format: RENDERED)
                      featuredImage {
                        node {
                          mediaItemUrl
                        }
                      }
                      title(format: RENDERED)
                    }
                  }
                  pageInfo {
                    endCursor
                    hasNextPage
                  }
                }
              }
            }"""
        }

        headers2 = {
            "Content-Type": "application/json",
            "Referer": "https://www.buaksib.com",
            "Origin": "https://www.buaksib.com"
        }

        response_ajax = requests.post(request_url, headers=headers2, json=payload)

        if response_ajax.status_code == 200:
            json_data = response_ajax.json()
            edges = json_data.get('data', {}).get('category', {}).get('posts', {}).get('edges', [])
            for edge in edges:
                node = edge.get("node", {})
                name = node.get("title", "N/A").strip()
                image = node.get("featuredImage", {}).get("node", {}).get("mediaItemUrl", "")
                slug = node.get("slug", "")
                raw_url = f"https://www.buaksib.com/highlights/{slug}/video/"

                final_url = fetch_video_links(raw_url)
                if not final_url:
                    continue
                if final_url in existing_urls:
                    print("⏩ เจอลิงก์ซ้ำ (GraphQL) หยุดการทำงาน")
                    break

                new_stations.append({
                    "name": f"⚽ {name}",
                    "image": image,
                    "url": final_url,
                    "referer": "https://www.buaksib.com/"
                })
                existing_urls.add(final_url)
                print(f"✅ เพิ่มจาก GraphQL: {name}")
        else:
            print(f"❌ ไม่สามารถโหลดข้อมูลเพิ่มเติมจาก GraphQL (status: {response_ajax.status_code})")

# รวมรายการใหม่+เดิม
if new_stations:
    print(f"🆕 เพิ่มรายการใหม่ {len(new_stations)} รายการ")
    data["stations"] = new_stations + stations_list
else:
    print("ℹ️ ไม่มีรายการใหม่")

data["author"] = f"update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


with open(m3u_file, 'w', encoding='utf-8') as f:
    m3u_content = "#EXTM3U\n"
    for station in data["stations"]:
        m3u_content += f'#EXTINF:-1 tvg-logo="{station["image"]}", group-title="LIVE SPORT", {station["name"].replace(":", "")}\n'
        m3u_content += f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36\n'
        m3u_content += f'#EXTVLCOPT:http-referrer={station["referer"]}\n'
        m3u_content += f'{station["url"]}\n'
    f.write(m3u_content)

print(f"✅ บันทึกไฟล์ {json_file} และ {m3u_file} เรียบร้อยแล้ว")
