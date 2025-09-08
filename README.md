# NUtv

ระบบอัปเดต Sport Rerun และสร้างไฟล์ JSON/M3U สำหรับ IPTV

## โครงสร้าง
- scripts/sport_rerun/ → เก็บสคริปต์ Python ดึงข้อมูล
- data/sport_rerun/ → เก็บไฟล์ JSON/M3U
- .github/workflows/ → Workflow GitHub Actions

## การใช้งาน
1. ตั้งค่า Secrets:
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID
2. Push โปรเจกต์ขึ้น GitHub
3. Workflow จะรันอัตโนมัติและส่งข้อความ Telegram

