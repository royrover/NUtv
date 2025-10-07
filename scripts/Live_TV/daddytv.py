import aiohttp
import asyncio
import json, re, os, platform
from bs4 import BeautifulSoup
from datetime import datetime

# ================= CONFIG =================
SYSTEM = platform.system()
if SYSTEM == "Windows":
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
else:  # Linux / Termux / GitHub
    SAVE_DIR = os.path.join(os.getcwd(), "data/live_tv")

os.makedirs(SAVE_DIR, exist_ok=True)
json_file = os.path.join(SAVE_DIR, "daddytv.json")
m3u_file = os.path.join(SAVE_DIR, "daddytv.m3u")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/91.0.4472.124 Safari/537.36"
}

# =============== FILE FUNCTIONS ===============
def load_old_data(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_new_data(path, data, m3u_path=None):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("📁 เขียนไฟล์เรียบร้อย:", path)

    if m3u_path and data.get("stations"):
        m3u = "#EXTM3U\n"
        for s in data["stations"]:
            m3u += (
                f'#EXTINF:-1 tvg-logo="{s["image"]}" group-title="Live TV",{s["name"]}\n'
                f'#EXTVLCOPT:http-referrer={s["referer"]}\n'
                f'#EXTVLCOPT:http-user-agent={s["userAgent"]}\n'
                f'{s["url"]}\n'
            )
        with open(m3u_path, "w", encoding="utf-8") as f:
            f.write(m3u)
        print("✅ M3U update done")

# =============== NETWORK HELPERS ===============
async def fetch_with_retry(session, url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers, timeout=30) as resp:
                if resp.status == 403:
                    print("🚫 Forbidden:", url)
                    return None
                resp.raise_for_status()
                return await resp.text()
        except aiohttp.ClientError as e:
            print(f"⚠️ Attempt {attempt+1}/{retries} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
    return None

async def get_referer(session):
    url = "https://daddylivestream.com/24-7-channels.php"
    html = await fetch_with_retry(session, url)
    if not html:
        return None, None, None

    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("div", class_="grid-container")
    if not container:
        return None, None, None

    first_channel = container.find("a")
    if not first_channel:
        return None, None, None

    try:
        channel_id = re.search(r"stream-(\d+)\.php", first_channel.get("href")).group(1)
        embed_url = f"https://dlhd.dad/embed/stream-{channel_id}.php"
        html_embed = await fetch_with_retry(session, embed_url)
        if not html_embed:
            return None, None, None
        match = re.search(r"https.*?daddyhd\.php\?id=\d+", html_embed)
        if not match:
            return None, None, None
        request_url = match.group(0)
        base_host = re.search(r"https://[^/]+", request_url).group(0)
        return request_url, base_host, html
    except Exception:
        return None, None, None

# =============== SCRAPE FUNCTION ===============
async def scrape_channel(session, ch, idx, total, headers_ref, base_host, data, sem):
    async with sem:
        name = ch.text.strip()
        href = ch.get("href", "")
        if not href or "18+" in name:
            return

        if any(s["name"] == name for s in data["stations"]):
            return  # skip duplicate

        try:
            channel_id = re.search(r"stream-(\d+)\.php", href).group(1)
        except:
            return

        print(f"{idx}/{total} 📺 {name} (ID:{channel_id})")

        embed_url = f"https://dlhd.dad/embed/stream-{channel_id}.php"
        html_embed = await fetch_with_retry(session, embed_url)
        if not html_embed:
            return
        match = re.search(r"https.*?daddyhd\.php\?id=\d+", html_embed)
        if not match:
            return
        request_url = match.group(0)

        try:
            async with session.get(request_url, headers=headers_ref) as resp:
                if resp.status != 200:
                    return
                html_content = await resp.text()
                match_key = re.search(r'const CHANNEL_KEY="([^"]+)";', html_content)
                if not match_key:
                    return
                channelKey = match_key.group(1)
        except:
            return

        lookup_url = f"{base_host}/server_lookup.php?channel_id={channelKey}"
        try:
            async with session.get(lookup_url, headers=headers_ref) as lresp:
                if lresp.status != 200:
                    return
                js = await lresp.json()
                sk = js.get("server_key", "")
                if not sk:
                    return
                if sk == "top1/cdn":
                    m3u8_url = f"https://top1.newkso.ru/top1/cdn/{channelKey}/mono.m3u8"
                else:
                    m3u8_url = f"https://{sk}new.newkso.ru/{sk}/{channelKey}/mono.m3u8"
        except:
            return

        data["stations"].append({
            "name": name,
            "image": data["image"],
            "url": m3u8_url,
            "referer": base_host + "/",
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) "
                         "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                         "Version/13.0.3 Mobile/15E148 Safari/604.1",
            "playInNatPlayer": "true",
        })

# =============== MAIN ===============
async def main():
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    old_data = load_old_data(json_file)

    async with aiohttp.ClientSession() as session:
        request_url, base_host, html = await get_referer(session)
        if not base_host:
            print("❌ ไม่พบ referer")
            return

        # ตรวจ referer เดิม
        if old_data and old_data.get("stations"):
            if old_data["stations"][0].get("referer", "") == base_host + "/":
                print("✅ referer ยังเหมือนเดิม → ใช้ไฟล์เก่า + update author")
                old_data["author"] = f"update {today}"
                save_new_data(json_file, old_data, m3u_file)
                return

        print("🔁 เริ่ม scrape ใหม่ทั้งหมด...")
        soup = BeautifulSoup(html, "html.parser")
        container = soup.find("div", class_="grid-container")

        data = {
            "name": "ช่องสด thedaddy",
            "image": "https://www.cg4tv.com/animation/stock-images-3d/world-map-animated-background.jpg",
            "url": "",
            "author": f"update {today}",
            "stations": [],
        }

        headers_ref = headers.copy()
        headers_ref["Referer"] = base_host + "/"
        channels = container.find_all("a")
        total = len(channels)
        sem = asyncio.Semaphore(8)  # จำกัด async 8 งานพร้อมกัน

        tasks = [
            scrape_channel(session, ch, idx, total, headers_ref, base_host, data, sem)
            for idx, ch in enumerate(channels, 1)
        ]
        await asyncio.gather(*tasks)

        if not data["stations"]:
            print("⚠️ ไม่มีช่องใดดึงได้ — ยกเลิกการเขียนไฟล์")
            return

        save_new_data(json_file, data, m3u_file)

# =============== RUN ===============
if __name__ == "__main__":
    asyncio.run(main())
