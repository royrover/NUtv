import os
import sys
import requests

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
    # กำหนดหลาย folder ผ่าน argument หรือ default
    folders = sys.argv[1:] or ["data/highlight_football", "data/sport_rerun"]

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN หรือ TELEGRAM_CHAT_ID ไม่ได้ตั้งค่า")
        sys.exit(1)

    message = "📁 อัปโหลดไฟล์สำเร็จ:\n\n"

    for folder_path in folders:
        try:
            files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
            if files:
                message += f"🏷️ หมวด: {folder_path}\n"
                for f in files:
                    message += f"✅ /{folder_path}/{f}\n"
                message += "\n"
            else:
                message += f"⚠️ หมวด: {folder_path} ไม่มีไฟล์ .json\n\n"
        except Exception as e:
            message += f"❌ เกิดข้อผิดพลาดในการอ่าน {folder_path}: {e}\n\n"

    send_telegram_message(bot_token, chat_id, message)
