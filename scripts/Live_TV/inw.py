import requests
from bs4 import BeautifulSoup
import os
import re
import platform
from urllib.parse import urljoin

# ================= CONFIG =================
SYSTEM = platform.system()
if SYSTEM == "Windows":
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    SAVE_DIR = os.path.join(os.getcwd(), "data/live_tv")

BASE_URL = "https://inwtv.site/views.php"
LOGIN_URL = "https://inwtv.site/login.php"

USERNAME = "ed0850641230"
PASSWORD = "0850641230"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

def login():
    session = requests.Session()
    payload = {"username": USERNAME, "password": PASSWORD, "remember": "1"}

    res = session.post(LOGIN_URL, data=payload, headers=HEADERS)
    print("\n============ HTML หลัง LOGIN ============\n")
    print(res.text)             # ⬅️  พิมพ์ HTML ทั้งหมด 100% ไม่ตัด
    print("\n============ END HTML ============\n")

    return session

def test_views(session):
    res = session.get(BASE_URL, headers=HEADERS)

    print("\n============ HTML ของ views.php ============\n")
    print(res.text)             # ⬅️  พิมพ์ HTML ทั้งหมดอีกหน้า
    print("\n============ END HTML ============\n")

if __name__ == "__main__":
    print("▶️ ทดสอบ login แล้ว print HTML เต็ม")

    session = login()
    test_views(session)
