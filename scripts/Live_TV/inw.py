import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin

# ================= CONFIG =================
SYSTEM = platform.system()
if SYSTEM == "Windows":
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
else:  # Linux / Termux / GitHub
    SAVE_DIR = os.path.join(os.getcwd(), "data/live_tv")

# ================= CONFIG =================
BASE_URL = "https://inwtv.site/views.php"
LOGIN_URL = "https://inwtv.site/login.php"
USERNAME = user_inw
PASSWORD = pass_inw
HEADERS = {"User-Agent": "Mozilla/5.0"}
M3U8_FOLDER = SAVE_DIR.

os.makedirs(M3U8_FOLDER, exist_ok=True)

# ================= HELPER =================
def sanitize_filename(name):
    """ลบอักขระไม่อนุญาตในชื่อไฟล์"""
    return re.sub(r'[<>:"/\\|?*]', "_", name)

def login():
    session = requests.Session()
    payload = {"username": USERNAME, "password": PASSWORD, "remember": "1"}
    try:
        res = session.post(LOGIN_URL, data=payload, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ ล็อกอินไม่สำเร็จ: {e}")
        return None
    print("✅ ล็อกอินสำเร็จ")
    return session

def scrape_channels(session):
    """ดึงรายการช่องหลักจาก views.php"""
    try:
        res = session.get(BASE_URL, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ ดึง {BASE_URL} ไม่สำเร็จ: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    channels = []
    for card in soup.select(".channel-card"):
        title = card.get("data-title", "").strip()
        onclick = card.get("onclick", "")
        id_match = re.search(r"id=(\d+)", onclick)
        if id_match:
            ch_id = id_match.group(1)
            channels.append({
                "title": title,
                "id": ch_id,
                "url": urljoin(BASE_URL, f"viewep.php?id={ch_id}")
            })
    print(f"🔍 พบ {len(channels)} ช่อง")
    return channels

def scrape_subchannels(session, viewep_url):
    """ดึง sub-channels จาก viewep.php?id=xxx"""
    try:
        res = session.get(viewep_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ ดึง {viewep_url} ไม่สำเร็จ: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    subchannels = []

    for card in soup.select(".channel-card"):
        h5_tag = card.find("h5")
        title = h5_tag.get_text(strip=True) if h5_tag else "NoTitle"
        onclick = card.get("onclick", "")
        id_match = re.search(r"ReadID\((\d+)\)", onclick)
        if id_match:
            sub_id = id_match.group(1)
            subchannels.append({
                "title": title,
                "id": sub_id
            })
    return subchannels

def get_hls_from_check(session, check_id):
    """ดึงลิงก์ HLS จาก check.php?id=xxx"""
    check_url = f"https://inwtv.site/check.php?id={check_id}"
    try:
        res = session.get(check_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
        if "hls" in data and data["hls"]:
            return data["hls"]
        # fallback regex
        m = re.search(r'https?://[^"\']+\.m3u8[^\s"\']*', res.text)
        if m:
            return m.group(0)
    except Exception as e:
        print(f"❌ ดึง HLS {check_id} ไม่สำเร็จ: {e}")
    return None

# ================= MAIN =================
if __name__ == "__main__":
    session = login()
    if not session:
        exit()

    channels = scrape_channels(session)

    # เก็บจำนวนชื่อซ้ำ
    name_counter = {}  # นับว่าชื่อแต่ละ safe_title ซ้ำกี่ครั้ง
    all_subchannels = []

    for ch in channels:
        subchannels = scrape_subchannels(session, ch["url"])
        for sub in subchannels:
            all_subchannels.append(sub)
            safe_title = sanitize_filename(sub["title"]).replace("Play ", " ")
            name_counter[safe_title] = name_counter.get(safe_title, 0) + 1

    # เก็บจำนวนไฟล์ที่สร้างแล้วสำหรับชื่อซ้ำ
    created_counter = {}

    for sub in all_subchannels:
        hls = get_hls_from_check(session, sub["id"])
        if not hls:
            continue

        safe_title = sanitize_filename(sub["title"])
        count = name_counter[safe_title]

        # ถ้าซ้ำ >1 ใช้ _1, _2
        if count > 1:
            created_counter[safe_title] = created_counter.get(safe_title, 0) + 1
            idx = created_counter[safe_title]
            filename = f"{M3U8_FOLDER}/{safe_title}_{idx}.m3u8"
        else:
            filename = f"{M3U8_FOLDER}/{safe_title}.m3u8"

        os.makedirs(M3U8_FOLDER, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("#EXT-X-VERSION:3\n")
            f.write("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=20000000\n")
            f.write(f"{hls}\n")
        print(f"✅ สร้างไฟล์ M3U8: {filename}")


