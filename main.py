import requests
from bs4 import BeautifulSoup
import os
import time

# ========= CONFIG =========
BOT_TOKEN = "5317731209:AAGu1NW-TdUP3m5UsNBoqx7O7gicreZRb6c"
CHAT_ID = "-1003761973494"

HSSC_URL = "https://hssc.gov.in/advertisement"
IGNOU_URL = "http://rcdelhi2.ignou.ac.in/aboutus/4"

FILE_HSSC = "hssc.txt"
FILE_IGNOU = "ignou.txt"
# ==========================


# ===== TELEGRAM =====
def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, data=data)


# ===== HSSC =====
def get_hssc():
    try:
        r = requests.get(HSSC_URL, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        table = soup.find("table")
        rows = table.find_all("tr")

        cols = rows[1].find_all("td")

        title = cols[0].text.strip()
        date = cols[1].text.strip()

        link = cols[0].find("a")
        if link:
            link = "https://hssc.gov.in" + link.get("href")
        else:
            link = ""

        return f"{title} ({date})\n{link}"

    except:
        return None


# ===== IGNOU =====
def get_ignou():
    try:
        r = requests.get("http://rcdelhi2.ignou.ac.in/aboutus/4", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # 🔍 Find notification section specifically
        notifications_section = soup.find("div", string="Notifications")

        # fallback: find all links under main content
        content = soup.find_all("a")

        for link in content:
            text = link.text.strip()
            href = link.get("href")

            # ✅ filter only real notifications
            if text.startswith("Notification"):

                if not href.startswith("http"):
                    href = "http://rcdelhi2.ignou.ac.in" + href

                return f"{text}\n{href}"

        return None

    except Exception as e:
        print("IGNOU error:", e)
        return None

# ===== CHECK FUNCTION =====
def check_updates():
    new_found = False

    # --- HSSC ---
    hssc = get_hssc()
    if hssc:
        old = open(FILE_HSSC).read() if os.path.exists(FILE_HSSC) else ""

        if hssc != old:
            send_message(f"🚨 HSSC Update\n\n{hssc}")
            open(FILE_HSSC, "w").write(hssc)
            new_found = True

    # --- IGNOU ---
    ignou = get_ignou()
    if ignou:
        old = open(FILE_IGNOU).read() if os.path.exists(FILE_IGNOU) else ""

        if ignou != old:
            send_message(f"📢 IGNOU Update\n\n{ignou}")
            open(FILE_IGNOU, "w").write(ignou)
            new_found = True

    # --- NO UPDATE ---
    if not new_found:
        send_message("❌ No new notification yet")


# ===== LOOP =====
if __name__ == "__main__":
    while True:
        print("Checking...")
        check_updates()
        time.sleep(28800)   # every 10 minutes
