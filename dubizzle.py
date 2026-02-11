import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# =========================
# إعدادات
# =========================

URL = "https://www.dubizzle.com.eg/en/mobile-phones-tablets-accessories-numbers/mobile-phones/alexandria/q-iphone/"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 30  # كل كام ثانية يعمل فحص

last_ad_link = None

# =========================
# إعداد المتصفح
# =========================

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)

# =========================
# إرسال رسالة تيليجرام
# =========================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

# =========================
# تشغيل المراقبة
# =========================

while True:
    try:
        driver.get(URL)
        time.sleep(5)

        ads = driver.find_elements(By.CSS_SELECTOR, "a[href*='/ad/']")

        if ads:
            first_ad = ads[0]
            link = first_ad.get_attribute("href")

            if link != last_ad_link:
                last_ad_link = link
                message = f"📢 إعلان جديد:\n{link}"
                send_telegram(message)
                print("New ad sent!")
            else:
                print("No new ad")

        else:
            print("No ads found")

    except Exception as e:
        print("Error:", e)

    time.sleep(CHECK_INTERVAL)
