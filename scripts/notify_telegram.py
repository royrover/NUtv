import os
import sys
import requests
import datetime
import time

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        print("✅ ส่งข้อความ Telegram สำเร็จ")
    except Exception as e:
        print(f"❌ ส่งข้อความ Telegram ไม่สำเร็จ: {e}")

if __name__ == "__main__":
    # folder หลายตัว
    folders = sys.argv[1:] or ["data/highlight_football", "data/sport_rerun"]

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN หรือ TELEGRAM_CHAT_ID ไม่ได้ตั้งค่า")
        exit(1)

    # ใช้ flag file + timestamp กันส่งซ้ำ
    FLAG_FILE = ".telegram_sent.flag"
    MAX_INTERVAL = 300  # 5 นาที
    send_allowed = True

    if os.path.exists(FLAG_FILE):
        try:
            last_sent = float(open(FLAG_FILE).read())
            if time.time() - last_sent < MAX_INTERVAL:
                send_allowed = False
        except:
            send_allowed = True  # ถ้าอ่านไฟล์ผิด ให้ส่ง

    if not send_allowed:
        print(f"✅ Telegram ส่งแล้วในช่วง {MAX_INTERVAL} วินาทีล่าสุด ไม่ส่งซ้ำ")
        exit(0)

    # เวลาปัจจุบัน +7 ชั่วโมงไทย
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    time_str = now.strftime("%d-%m-%Y %H:%M:%S")

    message = f"📁 อัปโหลดไฟล์สำเร็จ:\n\nเวลา: {time_str}\n\n"

    for folder_path in folders:
        try:
            files = [f for f in os.listdir(folder_path) if f.endswith((".json", ".m3u"))]
            files = sorted(set(files))  # ตัดไฟล์ซ้ำ
            if files:
                message += f"🏷️ หมวด: {folder_path}\n"
                for f in files:
                    message += f"✅ /{folder_path}/{f}\n"
                message += "\n"
            else:
                message += f"⚠️ หมวด: {folder_path} ไม่มีไฟล์\n\n"
        except Exception as e:
            message += f"❌ เกิดข้อผิดพลาดในการอ่าน {folder_path}: {e}\n\n"

    # ส่ง Telegram
    send_telegram_message(bot_token, chat_id, message)

    # อัปเดต flag file
    with open(FLAG_FILE, "w") as f:
        f.write(str(time.time()))
