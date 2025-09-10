import requests
import os
import sys
import logging
import time

# ตั้งค่า logging
logging.basicConfig(filename="telegram_notify.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def send_telegram_message(bot_token, chat_id, message, retries=3):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(url, data=payload, timeout=10)
            resp.raise_for_status()
            logging.info("✅ ส่งข้อความ Telegram สำเร็จ")
            print("✅ ส่งข้อความ Telegram สำเร็จ")
            return True
        except Exception as e:
            logging.warning(f"❌ ครั้งที่ {attempt} ส่งไม่สำเร็จ: {e}")
            print(f"❌ ครั้งที่ {attempt} ส่งไม่สำเร็จ: {e}")
            time.sleep(3)  # รอ 3 วินาทีแล้วลองใหม่
    logging.error("❌ ส่งข้อความ Telegram ไม่สำเร็จหลังจาก retry ทั้งหมด")
    return False

if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "สวัสดีจาก GitHub Action!"
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN หรือ TELEGRAM_CHAT_ID ไม่ได้ตั้งค่า")
        sys.exit(1)
    
    send_telegram_message(bot_token, chat_id, message)
