import os
import json
import time
import requests
from playwright.sync_api import sync_playwright

print("🚀 Bot is starting up...")

try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]
except KeyError as e:
    print(f"❌ Missing environment variable: {e}")
    exit(1)

# --- Load credentials from environment ---
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# --- Settings ---
KEYWORDS = ["specialized", "kona", "yt decoy", "trek", "santa cruz", "orbea", "norco"]
PRICE_MIN = 1000
PRICE_MAX = 3000
CHECK_INTERVAL = 600  # 10 minutes in seconds
SEEN_FILE = "seen_ads.json"
LOCATION_URL = "https://www.kijiji.ca/b-montreal/downtown/k0l80002?radius=25.0"

# --- Load seen ads from file ---
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_ads = set(json.load(f))
else:
    seen_ads = set()

# --- Telegram Message Sender ---
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=payload)
        print("📤 Sent Telegram message:", response.status_code)
    except Exception as e:
        print("⚠️ Failed to send Telegram message:", e)

# --- Main bot logic ---
def run_bot():
    global seen_ads

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

            print(f"📝 Title: {title} | Price: {price} | ID: {ad_id}")

            if ad_id in seen_ads:
                continue

            if any(k in title for k in KEYWORDS) and price and PRICE_MIN <= price <= PRICE_MAX:
                print("✅ New match found!")
                message = f"🔎 *Keyword match found!*\n\n📝 {title}\n💰 ${price}\n🔗 {url}"
                send_telegram_message(message)
                seen_ads.add(ad_id)

        # Save updated seen ads
        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen_ads), f)

        browser.close()

# --- Entry point ---
print("🚀 Bot is starting up...")

while True:
    try:
        print("⏱ Running bot...")
        run_bot()
        print(f"💤 Sleeping for {CHECK_INTERVAL // 60} minutes...\n")
    except Exception as e:
        import traceback
        print("❌ Bot crashed with error:")
        traceback.print_exc()
    time.sleep(CHECK_INTERVAL)
