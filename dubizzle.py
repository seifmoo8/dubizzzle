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

seen_links = set()  # حفظ الإعلانات المرسلة سابقاً

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
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram send error:", e)

# =========================
# تشغيل المراقبة
# =========================

print("🚀 بدأ المراقبة على Dubizzle...")

while True:
    try:
        driver.get(URL)
        time.sleep(5)

        ads = driver.find_elements(By.CSS_SELECTOR, "a[href*='/ad/']")

        # تجاهل الإعلانات المميزة
        normal_ads = []
        for ad in ads:
            classes = ad.get_attribute("class") or ""
            if "featured" not in classes:  # "featured" غالباً موجودة في الإعلانات المميزة
                normal_ads.append(ad)

        new_count = 0
        for ad in normal_ads:
            link = ad.get_attribute("href")
            if link not in seen_links:
                seen_links.add(link)
                title = ad.text.strip() or "إعلان جديد"
                send_telegram(f"📱 {title}\n{link}")
                print("✅ إعلان جديد:", link)
                new_count += 1

        if new_count == 0:
            print("لا توجد إعلانات جديدة في هذه الجولة.")

    except Exception as e:
        print("❌ خطأ:", e)

    time.sleep(CHECK_INTERVAL)
