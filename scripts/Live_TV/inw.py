import requests
from bs4 import BeautifulSoup
import os
import re
import platform
from urllib.parse import urljoin

# ================= CONFIG =================
SYSTEM = platform.system()
if SYSTEM == "Windows":
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
else:  # Linux / Termux / GitHub Action
    SAVE_DIR = os.path.join(os.getcwd(), "data/live_tv")

BASE_URL = "https://inwtv.site/views.php"
LOGIN_URL = "https://inwtv.site/login.php"

# อ่านจาก GitHub Actions Secrets
USERNAME = os.getenv("USER_INW")
PASSWORD = os.getenv("PASS_INW")

HEADERS = {"User-Agent": "Mozilla/5.0"}
M3U8_FOLDER = os.path.join(SAVE_DIR, "m3u8_files")

os.makedirs(M3U8_FOLDER, exist_ok=True)

# ================= HELPER =================
def sanitize_filename(name):
    """ลบอักขระไม่อนุญาตในชื่อไฟล์"""
    name = name.replace("Play ", "")  # 🔥 เอา Play ออก
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()

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
            subchannels.append({"title": title, "id": id_match.group(1)})

    return subchannels

def get_hls_from_check(session, check_id):
    check_url = f"https://inwtv.site/check.php?id={check_id}"

    try:
        res = session.get(check_url, headers=HEADERS, timeout=10)
        res.raise_for_status()

        try:
            data = res.json()
            if "hls" in data and data["hls"]:
                return data["hls"]
        except:
            pass

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

    name_counter = {}
    all_subchannels = []

    for ch in channels:
        subs = scrape_subchannels(session, ch["url"])

        for sub in subs:
            safe_title = sanitize_filename(sub["title"])
            name_counter[safe_title] = name_counter.get(safe_title, 0) + 1
            all_subchannels.append(sub)

    created_counter = {}

    for sub in all_subchannels:
        hls = get_hls_from_check(session, sub["id"])
        if not hls:
            continue

        safe_title = sanitize_filename(sub["title"])

        if name_counter[safe_title] > 1:
            created_counter[safe_title] = created_counter.get(safe_title, 0) + 1
            idx = created_counter[safe_title]
            filename = f"{M3U8_FOLDER}/{safe_title}_{idx}.m3u8"
        else:
            filename = f"{M3U8_FOLDER}/{safe_title}.m3u8"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("#EXT-X-VERSION:3\n")
            f.write("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=20000000\n")
            f.write(f"{hls}\n")

        print(f"✅ สร้างไฟล์ M3U8: {filename}")



