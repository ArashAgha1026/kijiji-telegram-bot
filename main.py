print("🚀 Bot is starting up...")
import os
import requests
import json
import time
from playwright.sync_api import sync_playwright

# Read sensitive values from environment
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

KEYWORDS = ["specialized", "kona", "yt decoy", "trek", "santa cruz", "orbea", "norco"]
PRICE_MIN = 1000
PRICE_MAX = 3000
CHECK_INTERVAL = 600  # 10 minutes
SEEN_FILE = "seen_ads.json"
LOCATION_URL = "https://www.kijiji.ca/b-montreal/downtown/k0l80002?radius=25.0"

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_ads = set(json.load(f))
else:
    seen_ads = set()

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

def run_bot():
    global seen_ads
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(LOCATION_URL)
        page.wait_for_timeout(5000)

        ads = page.query_selector_all("li[data-listing-id]")
        print(f"Found {len(ads)} ads")

        for ad in ads:
            title_el = ad.query_selector("h3") or ad.query_selector("div.title")
            price_el = ad.query_selector("div.price") or ad.query_selector("span.price")

            if not title_el:
                continue

            title = title_el.inner_text().lower()
            link_el = ad.query_selector("a")
            url = "https://www.kijiji.ca" + link_el.get_attribute("href") if link_el else "no link"

            try:
                price = int(price_el.inner_text().replace("$", "").replace(",", "").strip())
            except:
                price = None

            ad_id = url.split("/")[-1]
            if ad_id in seen_ads:
                continue

            if any(k in title for k in KEYWORDS) and price and PRICE_MIN <= price <= PRICE_MAX:
                print(f"✅ Match: {title} - ${price}")
                send_telegram_message(f"✅ Match:\n{title}\n💰 ${price}\n🔗 {url}")
                seen_ads.add(ad_id)

        browser.close()

        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen_ads), f)

# Loop forever
while True:
    try:
        run_bot()
    except Exception as e:
        print("Error:", e)
    time.sleep(CHECK_INTERVAL)
