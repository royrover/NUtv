# 📺 NUtv

🎉 ระบบอัปเดต **Sport Rerun** และสร้างไฟล์ **JSON/M3U** สำหรับ IPTV อัตโนมัติ  

---

## 🗂️ โครงสร้างโปรเจกต์

| โฟลเดอร์ | รายละเอียด |
|-----------|------------|
| `scripts/sport_rerun/` | เก็บสคริปต์ Python ดึงข้อมูลจากเว็บไซต์ต่าง ๆ |
| `data/sport_rerun/`    | เก็บไฟล์ JSON / M3U ที่สร้างขึ้น |
| `.github/workflows/`    | GitHub Actions Workflow สำหรับรันอัตโนมัติ |

---

## ⚙️ การใช้งาน

### 1️⃣ ตั้งค่า GitHub Secrets

| Secret | รายละเอียด |
|--------|------------|
| `TELEGRAM_BOT_TOKEN` | Token ของ Telegram Bot สำหรับส่งข้อความแจ้งสถานะ |
| `TELEGRAM_CHAT_ID`   | Chat ID ของกลุ่มหรือผู้รับข้อความ Telegram |
| `GITHUB_TOKEN`       | GitHub สร้างให้อัตโนมัติใน Actions |

---

### 2️⃣ Push โปรเจกต์ขึ้น GitHub

- Workflow จะรันตามเวลาที่กำหนดใน `.yml` เช่น **07:00 และ 19:00 ไทย**  
- จะติดตั้ง dependencies อัตโนมัติและรันสคริปต์ทั้งหมด:

```bash
pip install --upgrade pip
pip install requests beautifulsoup4 lxml python-telegram-bot dropbox

3️⃣ ส่งข้อความแจ้งเตือนทาง Telegram

หลังจากอัปเดตไฟล์ JSON/M3U จะส่งข้อความพร้อมรายการไฟล์ที่อัปเดต ✅

📁 อัปโหลดไฮไลท์ฟุตบอลสำเร็จ:

✅ /New Wiseplay/Highlight Football/acdsport_replay.json
✅ /New Wiseplay/Highlight Football/dookeela_rerun.json
✅ /New Wiseplay/Highlight Football/goaldaddyth.json

🎉 อัปโหลดทั้งหมดเสร็จสิ้นแล้ว 07-09-2025 13:07:38

4️⃣ Commit & Push Workflow Updates

ถ้ามีการแก้ไขสคริปต์หรือ workflow:

git add .
git commit -m "แก้ไข workflow / scripts"
git push

Workflow จะอัปเดตไฟล์ JSON/M3U และแจ้ง Telegram อัตโนมัติ 🎯
