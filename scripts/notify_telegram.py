import requests
import os
import sys

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
        print("✅ ส่งข้อความ Telegram สำเร็จ")
    except Exception as e:
        print(f"❌ ส่งข้อความ Telegram ไม่สำเร็จ: {e}")

if __name__ == "__main__":
    # รับค่า arguments จาก workflow
    message = sys.argv[1] if len(sys.argv) > 1 else "สวัสดีจาก GitHub Action!"
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN หรือ TELEGRAM_CHAT_ID ไม่ได้ตั้งค่า")
        sys.exit(1)
    
    send_telegram_message(bot_token, chat_id, message)
