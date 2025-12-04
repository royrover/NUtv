from pathlib import Path
import re
import os
import requests
from bs4 import BeautifulSoup

# ===== FIX: PATH สำหรับ GitHub Actions =====
PROJECT_ROOT = Path(__file__).resolve().parents[2]   # repo root เสมอ
BASE_DIR = PROJECT_ROOT / "data" / "live_tv"
M3U8_FOLDER = BASE_DIR / "m3u8_file"
M3U8_FOLDER.mkdir(parents=True, exist_ok=True)

print("📂 PROJECT_ROOT     :", PROJECT_ROOT)
print("📂 M3U8_FOLDER      :", M3U8_FOLDER)

# ===== CONFIG LOGIN =====
USERNAME = os.getenv("USER_INW")
PASSWORD = os.getenv("PASS_INW")

BASE_URL = "https://app.inwtv.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ===== HELPER =====
def sanitize_filename(name):
    return re.sub(r'[\\/:"*?<>|]+', "_", name)

def get_hls_from_check(session, channel_id):
    check_url = f"{BASE_URL}/play?id={channel_id}"
    try:
        res = session.get(check_url, headers=HEADERS, timeout=10)

        # JSON จาก /play
        try:
            j = res.json()
            if j.get("hls"):
                return j["hls"]
        except:
            pass

        # HTML m3u8
        m = re.search(r'https?://[^"\']+\.m3u8[^\s"\']*', res.text)
        if m:
            return m.group(0)

    except Exception as e:
        print(f"❌ ดึง HLS {channel_id} ไม่สำเร็จ:", e)
    return None


# ===== START SESSION =====
session = requests.Session()

# GET CSRF
home_html = session.get(BASE_URL, headers=HEADERS).text
soup = BeautifulSoup(home_html, "html.parser")
csrf_input = soup.find("input", {"name": "csrf_tv_name"})

if not csrf_input:
    raise Exception("❌ ไม่พบ CSRF token")

csrf = csrf_input["value"]

# LOGIN
payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "remember": "1",
    "csrf_tv_name": csrf,
}

login_res = session.post(f"{BASE_URL}/authen", data=payload, headers=HEADERS)

cookies = session.cookies.get_dict()
print("🍪 COOKIES:", cookies)

if not any(k.startswith("ci_session") for k in cookies.keys()):
    raise Exception("❌ Login ล้มเหลว — ไม่มี ci_session")

print("✅ Login สำเร็จ\n")


# ===== CATEGORY MAP =====
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

# ===== SCRAPE =====
channels = {}

for main_cat, subcats in category_urls.items():
    print(f"=== {main_cat} ===")
    channels[main_cat] = {}

    for sub_name, url in subcats.items():
        print(f"-- {sub_name} --")

        resp = session.get(url, headers=HEADERS)
        soup_c = BeautifulSoup(resp.text, "html.parser")

        cmap = {}

        # FIX: รองรับรูปแบบ href ทั้งหมด
        for a in soup_c.find_all("a", href=True):
            href = a["href"]

            m = re.search(r"Play\((\d+)\)", href)
            if not m:
                continue

            cid = m.group(1)
            cname = a.text.strip()
            if cname:
                cmap[cname] = cid
                print("   •", cname)

        channels[main_cat][sub_name] = cmap


# ===== WRITE M3U8 =====
# STEP 4: CREATE M3U8 FILES
print("=== สร้างไฟล์ M3U8 ===")

count_written = 0

for main_cat, subcats in channels_by_category.items():
    for sub_name, ch_dict in subcats.items():
        for ch_name, ch_id in ch_dict.items():

            safe = sanitize_filename(ch_name)
            hls = get_hls_from_check(session, ch_id)

            if not hls:
                print(f"❌ ไม่มี HLS: {ch_name}")
                continue

            file_path = M3U8_FOLDER / f"{safe}.m3u8"

            # 🔥 คืนรูปแบบ logic M3U8 ตามที่คุณณุเขียนไว้เดิม
            content = (
                "#EXTM3U\n"
                "#EXT-X-VERSION:3\n"
                "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=20000000\n"
                f"{hls}\n"
            )

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ เขียนไฟล์: {file_path.name}")
                count_written += 1

            except Exception as e:
                print(f"❌ เขียนไฟล์ไม่สำเร็จ {file_path}: {e}")

print(f"\n🎉 สร้างไฟล์ M3U8 สำเร็จทั้งหมด {count_written} ไฟล์")
