import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json, re, os, platform
from datetime import datetime

SYSTEM = platform.system()
SAVE_DIR = os.path.dirname(os.path.abspath(__file__)) if SYSTEM=="Windows" else "/storage/emulated/0/htdocs/PYTHON/live_sport/livetv/Livetv"
os.makedirs(SAVE_DIR, exist_ok=True)

json_file = os.path.join(SAVE_DIR, "daddytv.json")
m3u_file = os.path.join(SAVE_DIR, "daddytv.m3u")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

def load_old_data(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None

def save_new_data(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)
    print("📁 เขียนไฟล์เรียบร้อย:", path)

async def fetch_with_retry(session,url,retries=3,delay=5):
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers, timeout=30) as resp:
                if resp.status==403:
                    print("🚫 Forbidden:", url)
                    return None
                resp.raise_for_status()
                return await resp.text()
        except aiohttp.ClientError as e:
            print(f"⚠️ Attempt {attempt+1}/{retries} failed: {e}")
            if attempt<retries-1: await asyncio.sleep(delay)
    return None

async def get_referer(session):
    url="https://daddylivestream.com/24-7-channels.php"
    html = await fetch_with_retry(session,url)
    if not html: return None,None,None
    soup = BeautifulSoup(html,"html.parser")
    container = soup.find("div",class_="grid-container")
    if not container: return None,None,None
    first_channel = container.find("a")
    if not first_channel: return None,None,None
    try:
        channel_id = re.search(r"stream-(\d+)\.php", first_channel.get("href")).group(1)
        embed_url = f"https://dlhd.dad/embed/stream-{channel_id}.php"
        html_embed = await fetch_with_retry(session,embed_url)
        if not html_embed: return None,None,None
        match = re.search(r"https.*?daddyhd\.php\?id=\d+", html_embed)
        if not match: return None,None,None
        request_url = match.group(0)
        base_host = re.search(r"https://[^/]+",request_url).group(0)
        return request_url, base_host, html
    except:
        return None,None,None

async def main():
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    old_data = load_old_data(json_file)
    async with aiohttp.ClientSession() as session:
        request_url, base_host, html = await get_referer(session)
        if not base_host: print("❌ ไม่พบ referer"); return
        if old_data and old_data.get("stations"):
            if old_data["stations"][0].get("referer","")==base_host+"/":
                print("✅ referer ยังเหมือนเดิม → ใช้ไฟล์เก่า + update author")
                old_data["author"]=f"update {today}"
                save_new_data(json_file,old_data)
                return

        print("🔁 scrape ใหม่ทั้งหมด")
        soup = BeautifulSoup(html,"html.parser")
        container = soup.find("div",class_="grid-container")
        data={
            "name":"ช่องสด thedaddy",
            "image":"https://www.cg4tv.com/animation/stock-images-3d/world-map-animated-background.jpg",
            "url":"",
            "author":f"update {today}",
            "stations":[],
        }
        headers_ref = headers.copy()
        headers_ref["Referer"]=base_host+"/"
        channels = [ch for ch in container.find_all("a") if "18+" not in ch.text]
        total=len(channels)

        for idx,ch in enumerate(channels,1):
            name = ch.text.strip()
            href = ch.get("href","")
            if not href: continue
            try: channel_id = re.search(r"stream-(\d+)\.php",href).group(1)
            except: continue
            print(f"{idx}/{total} 📺 {name} ID:{channel_id}")

            embed_url = f"https://dlhd.dad/embed/stream-{channel_id}.php"
            html_embed = await fetch_with_retry(session,embed_url)
            if not html_embed: continue
            match = re.search(r"https.*?daddyhd\.php\?id=\d+",html_embed)
            if not match: continue
            request_url = match.group(0)

            async with session.get(request_url,headers=headers_ref) as resp:
                if resp.status!=200: continue
                html_content = await resp.text()
                match_key = re.search(r'const CHANNEL_KEY="([^"]+)";',html_content)
                if not match_key: continue
                channelKey = match_key.group(1)

                lookup_url=f"{base_host}/server_lookup.php?channel_id={channelKey}"
                async with session.get(lookup_url,headers=headers_ref) as lresp:
                    if lresp.status!=200: continue
                    sk = (await lresp.json()).get("server_key","")
                    if not sk: continue
                    m3u8_url = f"https://top1.newkso.ru/top1/cdn/{channelKey}/mono.m3u8" if sk=="top1/cdn" else f"https://{sk}new.newkso.ru/{sk}/{channelKey}/mono.m3u8"
                    data["stations"].append({
                        "name":name,
                        "image":data["image"],
                        "url":m3u8_url,
                        "referer":base_host+"/",
                        "userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
                        "playInNatPlayer":"true"
                    })

        save_new_data(json_file,data)

        # สร้าง M3U
        m3u = "#EXTM3U\n"
        for s in data["stations"]:
            m3u += f'#EXTINF:-1 code="external" tvg-logo="{s["image"]}" group-title="Live TV",{s["name"]}\n'
            m3u += f'#EXTVLCOPT:http-referrer={s["referer"]}\n'
            m3u += f'#EXTVLCOPT:http-user-agent={s["userAgent"]}\n{s["url"]}\n'

        with open(m3u_file,"w",encoding="utf-8") as f:
            f.write(m3u)
        print("✅ M3U update done")

asyncio.run(main())
