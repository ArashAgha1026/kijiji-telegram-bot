import os
import json
import time
import requests
from playwright.sync_api import sync_playwright

print("🚀 Starting bot setup...")

# Step 1: Startup message
print("🛠 Bot is running this line!")

# Step 2: Test Telegram connection
try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]
    test_message = "✅ Telegram bot has started successfully."
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": test_message}
    )
    print("📤 Telegram startup message sent")
except Exception as e:
    print("❌ Telegram send failed:", e)
    exit(1)

# Step 3: Confirm setup complete
print("✅ Setup successful. Proceeding to Kijiji scraping...")

# --- Scraping settings ---
KEYWORDS = ["specialized", "kona", "yt decoy", "trek", "santa cruz", "orbea", "norco"]
PRICE_MIN = 1000
PRICE_MAX = 3000
CHECK_INTERVAL = 600
SEEN_FILE = "seen_ads.json"
LOCATION_URL = "https://www.kijiji.ca/b-montreal/downtown/k0l80002?radius=25.0"

try:
    with open(SEEN_FILE, "r") as f:
        seen_ads = set(json.load(f))
except:
    seen_ads = set()

def send_telegram_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text}
        )
        print("📤 Sent to Telegram")
    except Exception as e:
        print("❌ Error sending to Telegram:", e)

def run_bot():
    global seen_ads
    print("🧠 Scraping", LOCATION_URL)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(LOCATION_URL)
        page.wait_for_timeout(5000)

        ads = page.query_selector_all("li[data-listing-id]")
        print(f"🔍 Found {len(ads)} ads")

        for ad in ads:
            title_el = ad.query_selector("h3") or ad.query_selector("div.title")
            price_el = ad.query_selector("div.price") or ad.query_selector("span.price")
            link_el = ad.query_selector("a")

            if not title_el or not link_el:
                continue

            title = title_el.inner_text().lower()
            url = "https://www.kijiji.ca" + link_el.get_attribute("href")
            ad_id = url.split("/")[-1]

            try:
                price = int(price_el.inner_text().replace("$", "").replace(",", "").strip())
            except:
                price = None

            print(f"📝 {title} | ${price} | ID: {ad_id}")

            if ad_id in seen_ads:
                continue

            if any(k in title for k in KEYWORDS) and price and PRICE_MIN <= price <= PRICE_MAX:
                print("✅ Match found!")
                send_telegram_message(f"🆕 Match: {title}\n💰 ${price}\n🔗 {url}")
                seen_ads.add(ad_id)

        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen_ads), f)

        browser.close()

# --- Run forever loop ---
while True:
    try:
        print("🔁 Entering scraping loop...")
        run_bot()
        print("⏳ Sleeping for 10 minutes...\n")
        time.sleep(CHECK_INTERVAL)
    except Exception as e:
        import traceback
        print("🔥 Bot error:")
        traceback.print_exc()
        time.sleep(60)
