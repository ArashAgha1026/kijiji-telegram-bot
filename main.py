import os
import json
import time
import requests
from playwright.sync_api import sync_playwright

# --- Logger ---
def log_and_send(message):
    print(message, flush=True)
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
    except Exception as e:
        print(f"❌ Failed to send to Telegram: {e}", flush=True)

# --- Startup ---
print("🚀 Starting bot setup...", flush=True)

try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]
    log_and_send("✅ Telegram bot has started successfully.")
except Exception as e:
    print(f"❌ Missing env variable: {e}", flush=True)
    exit(1)

log_and_send("⚙️ Entering main scraping loop...")

# --- Config ---
KEYWORDS = ["specialized", "kona", "yt decoy", "trek", "santa cruz", "orbea", "norco"]
PRICE_MIN = 1000
PRICE_MAX = 3000
CHECK_INTERVAL = 600
SEEN_FILE = "seen_ads.json"
BASE_URL = "https://www.kijiji.ca/b-velos/ville-de-montreal/c644l1700281?radius=25.0&address=Montreal%2C+QC&ll=45.5018869%2C-73.56739189999999&view=list&keywords="

try:
    with open(SEEN_FILE, "r") as f:
        seen_ads = set(json.load(f))
except:
    seen_ads = set()

# --- Telegram sender ---
def send_telegram_message(text):
    log_and_send(text)

# --- Scraper ---
def run_bot():
    global seen_ads
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for keyword in KEYWORDS:
            search_url = BASE_URL + keyword.replace(" ", "+")
            log_and_send(f"🔍 Searching for '{keyword}' → {search_url}")
            page.goto(search_url)
            page.wait_for_timeout(5000)

            # Take screenshot for debugging
            screenshot_path = f"debug_{keyword}.png"
            page.screenshot(path=screenshot_path)
            log_and_send(f"📸 Screenshot saved: {screenshot_path}")

            # Try multiple selectors safely
            ads = page.query_selector_all("li[data-testid='listing-card']")
            if not ads:
                ads = page.query_selector_all("li[data-listing-id']")
            if not ads:
                ads = page.query_selector_all("div.search-item")

            log_and_send(f"🔎 Found {len(ads)} ads for '{keyword}'")

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

                log_and_send(f"📝 {title} | ${price} | ID: {ad_id}")

                if ad_id in seen_ads:
                    continue

                if keyword in title and price and PRICE_MIN <= price <= PRICE_MAX:
                    log_and_send("✅ Match found!")
                    send_telegram_message(f"🆕 Match: {title}\n💰 ${price}\n🔗 {url}")
                    seen_ads.add(ad_id)

        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen_ads), f)

        browser.close()

# --- Loop ---
while True:
    try:
        log_and_send("🔁 Starting scraping cycle...")
        run_bot()
        log_and_send("⏳ Sleeping for 10 minutes...\n")
        time.sleep(CHECK_INTERVAL)
    except Exception as e:
        import traceback
        log_and_send("🔥 Bot error:")
        traceback.print_exc()
        time.sleep(60)
