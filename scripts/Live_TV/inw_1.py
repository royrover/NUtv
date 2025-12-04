from pathlib import Path
import re
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ===== CONFIG PATH =====
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # ../../..
BASE_DIR = PROJECT_ROOT / "data" / "live_tv"
M3U8_FOLDER = BASE_DIR / "m3u8_file"
M3U8_FOLDER.mkdir(parents=True, exist_ok=True)

print("📂 โฟลเดอร์เก็บไฟล์ M3U8:", M3U8_FOLDER)

# ===== CONFIG LOGIN =====
# อ่านจาก Environment Variable (GitHub Actions / Termux / Linux)
USERNAME = os.getenv("USER_INW")
PASSWORD = os.getenv("PASS_INW")
BASE_URL = "https://inwtv.site"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# ===== HELPER =====
def sanitize_filename(name):
    return re.sub(r'[\\/:"*?<>|]+', "_", name)

def get_hls_from_check(session, channel_id):
    check_url = f"{BASE_URL}/play?id={channel_id}"
    try:
        res = session.get(check_url, headers=HEADERS, timeout=10)
        res.raise_for_status()

        # 1) ถ้ามี JSON พร้อม hls
        try:
            data = res.json()
            if "hls" in data and data["hls"]:
                return data["hls"]
        except:
            pass

        # 2) ถ้าเจอใน source HTML (ฝั่งเว็บ)
        m = re.search(r'https?://[^"\']+\.m3u8[^\s"\']*', res.text)
        if m:
            return m.group(0)

    except Exception as e:
        print(f"❌ ดึง HLS {channel_id} ไม่สำเร็จ: {e}")
    return None


# ===== START SESSION =====
session = requests.Session()

# STEP 0: GET CSRF TOKEN
home_html = session.get(BASE_URL, headers=HEADERS).text
soup = BeautifulSoup(home_html, "html.parser")
csrf_input = soup.find("input", {"name": "csrf_tv_name"})
if not csrf_input:
    raise Exception("❌ ไม่พบ CSRF token")
csrf = csrf_input["value"]

# STEP 1: LOGIN
login_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "remember": "1",
    "csrf_tv_name": csrf
}

login_res = session.post(f"{BASE_URL}/authen", data=login_payload, headers=HEADERS)
if "ci_session" not in session.cookies.get_dict():
    raise Exception("❌ Login ไม่สำเร็จ")

print("✅ Login สำเร็จ\n")


# STEP 2: CATEGORIES
category_urls = {
    "Thai": {
        "Sports": f"{BASE_URL}/live?fid=4&type=7",
        "Digital": f"{BASE_URL}/live?fid=4&type=1",
        "Cartoon": f"{BASE_URL}/live?fid=4&type=2",
        "Documentary": f"{BASE_URL}/live?fid=4&type=3",
        "Entertainment": f"{BASE_URL}/live?fid=4&type=4",
        "News": f"{BASE_URL}/live?fid=4&type=6",
    },
    "Foreign": {
        "Sports": f"{BASE_URL}/live?fid=90&type=1",
        "Entertainment": f"{BASE_URL}/live?fid=90&type=2",
        "Cartoon": f"{BASE_URL}/live?fid=90&type=3",
        "News": f"{BASE_URL}/live?fid=90&type=4",
    }
}

# STEP 3: SCRAPE CHANNEL LIST
channels_by_category = {}

for main_cat, subcats in category_urls.items():
    print(f"=== {main_cat} ===")
    channels_by_category[main_cat] = {}

    for sub_name, url in subcats.items():
        print(f"-- {sub_name} --")

        resp = session.get(url, headers=HEADERS)
        soup_c = BeautifulSoup(resp.text, "html.parser")

        channel_map = {}
        for a in soup_c.find_all("a", href=True):
            href = a["href"]
            if "javascript:Play" in href:
                cid = re.search(r"javascript:Play\((\d+)\)", href).group(1)
                cname = a.text.strip()
                channel_map[cname] = cid
                print("  •", cname)

        channels_by_category[main_cat][sub_name] = channel_map

    print("")

# STEP 4: CREATE M3U8 FILES
print("=== สร้างไฟล์ M3U8 ===")

for main_cat, subcats in channels_by_category.items():
    for sub_name, ch_dict in subcats.items():
        for ch_name, ch_id in ch_dict.items():

            safe = sanitize_filename(ch_name)
            hls = get_hls_from_check(session, ch_id)
            if not hls:
                print(f"❌ ไม่มี HLS: {ch_name}")
                continue
