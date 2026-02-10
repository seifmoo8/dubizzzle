from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, json, os, requests, re, random

# ===== إعدادات =====
URL = "https://www.dubizzle.com.eg/en/mobile-phones-tablets-accessories-numbers/mobile-phones/alexandria/q-iphone/"
SEEN_FILE = "seen_ids.json"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_DELAY = 30          # الأساس 30 ثانية
JITTER = 6               # ± عشوائي
RESTART_EVERY = 150      # Restart أسرع لأننا أسرع

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]

# ===== تحميل الإعلانات القديمة =====
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_ids = set(json.load(f))
else:
    seen_ids = set()

# ===== تلجرام =====
def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except:
        pass

# ===== Driver =====
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    return webdriver.Chrome(options=options)

driver = create_driver()
wait = WebDriverWait(driver, 15)
cycle = 0

print("🚀 Dubizzle watcher (30s safe) بدأ")

while True:
    try:
        cycle += 1
        driver.get(URL)

        # استنى تحميل الروابط
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/ad/')]")))
        time.sleep(2)

        # Scroll خفيف
        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

        cards = driver.find_elements(By.XPATH, "//a[contains(@href,'/ad/')]")

        new_ads = 0

        for a in cards:
            href = a.get_attribute("href")
            if not href:
                continue

            if "featured" in href.lower():
                continue

            m = re.search(r"ID(\d+)", href)
            if not m:
                continue
            ad_id = m.group(1)

            if ad_id in seen_ids:
                continue

            # نحاول نطلع بيانات من نفس الكارت
            title = a.text.strip() or "إعلان جديد"

            # السعر (محاولات مرنة)
            price = "غير محدد"
            try:
                price_el = a.find_element(By.XPATH, ".//*[contains(text(),'EGP') or contains(text(),'جنيه')]")
                price = price_el.text.strip()
            except:
                pass

            # المكان
            location = "غير محدد"
            try:
                loc_el = a.find_element(By.XPATH, ".//*[contains(@class,'location') or contains(text(),'Alexandria')]")
                location = loc_el.text.strip()
            except:
                pass

            seen_ids.add(ad_id)
            new_ads += 1

            msg = (
                "📱 إعلان جديد على Dubizzle\n"
                f"📝 {title}\n"
                f"💰 السعر: {price}\n"
                f"📍 المكان: {location}\n"
                f"🔗 {href}"
            )
            send_telegram(msg)
            print("✅ جديد:", ad_id, price, location)

        if new_ads:
            with open(SEEN_FILE, "w") as f:
                json.dump(list(seen_ids), f)
            print(f"📨 اتبعت {new_ads} إعلان")

        # Restart دوري
        if cycle % RESTART_EVERY == 0:
            print("🔄 Restart driver")
            driver.quit()
            driver = create_driver()
            wait = WebDriverWait(driver, 15)

    except Exception as e:
        print("❌ خطأ:", e)
        try:
            driver.quit()
        except:
            pass
        driver = create_driver()
        wait = WebDriverWait(driver, 15)

    time.sleep(BASE_DELAY + random.randint(-JITTER, JITTER))
