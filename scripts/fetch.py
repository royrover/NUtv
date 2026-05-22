import os
import cloudscraper

# URL ต้นทางที่ต้องการเจาะ
url = "https://ipplaybox.fun/dookeela/ch3hd/chunks.m3u8"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://ipplaybox.fun/",
}

try:
    # ใช้ cloudscraper ทะลวงด่าน Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True}
    )
    response = scraper.get(url, headers=headers, timeout=15)
    
    if response.status_code == 200 and "#EXTM3U" in response.text:
        raw_content = response.text
        
        # แก้ไขเนื้อหาในนี้ให้เปลี่ยนจาก .css เป็น .ts และชี้เป้าไปที่เว็บตรงเลย
        # (เพราะถ้า .m3u8 ผ่านแล้ว บางทีไฟล์วิดีโอ .css ยิงตรงอาจจะไม่ติดบล็อก)
        lines = raw_content.split("\n")
        new_lines = []
        base_url = "https://ipplaybox.fun/dookeela/ch3hd/"
        
        for line in lines:
            t = line.strip()
            if t and not t.startswith("#"):
                # เปลี่ยน .css เป็น .ts ทันที
                if ".css" in t:
                    t = t.replace(".css", ".ts")
                # ทำเป็นลิงก์เต็มรูปแบบ
                if not t.startswith("http"):
                    t = base_url + t
            new_lines.append(t)
            
        processed_content = "\n".join(new_lines)
        
        # เซฟไฟล์ออกมาเป็นชื่อ live.m3u8
        with open("live.m3u8", "w", encoding="utf-8") as f:
            f.write(processed_content)
        print("Fetch and Convert Successful!")
    else:
        print(f"Failed to fetch. Status code: {response.status_code}")
except Exception as e:
    print(f"Error occurred: {e}")
