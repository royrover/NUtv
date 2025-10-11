import aiohttp
import asyncio
import re
import json
import os

SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
json_file = os.path.join(SAVE_DIR, "channel_images.json")

M3U_URL = "https://raw.githubusercontent.com/Metroid2023/DaddyLiveHD/refs/heads/main/playlist.m3u8"

async def fetch_m3u(session, url):
    async with session.get(url) as resp:
        resp.raise_for_status()
        return await resp.text()

async def main():
    async with aiohttp.ClientSession() as session:
        text = await fetch_m3u(session, M3U_URL)
        lines = text.splitlines()

        channels = []
        for i, line in enumerate(lines):
            if line.startswith("#EXTINF"):
                # ตัวอย่าง: #EXTINF:-1 tvg-id="channel.id" tvg-logo="https://..." group-title="..." ,Channel Name
                match = re.search(r'tvg-id="([^"]*)".*tvg-logo="([^"]*)".*,(.+)', line)
                if match:
                    tvg_id, img_url, name = match.groups()
                    channels.append({
                        "name": name.strip(),
                        "tvg-id": tvg_id.strip(),
                        "image": img_url.strip()
                    })

        # เขียน JSON
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=4)
        print(f"✅ สร้าง JSON เรียบร้อย: {json_file}, จำนวนช่อง: {len(channels)}")

if __name__ == "__main__":
    asyncio.run(main())
