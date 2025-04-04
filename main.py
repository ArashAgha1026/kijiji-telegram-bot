import os
import time
import requests

def log_and_send(message):
    print(message, flush=True)
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )
    except Exception as e:
        print(f"❌ Failed to send to Telegram: {e}", flush=True)

print("🚀 Bot starting", flush=True)

try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]
    log_and_send("🔄 Bot has entered the main loop!")
except Exception as e:
    print("❌ Failed to send startup message:", e, flush=True)
    exit(1)

log_and_send("⚙️ Entering loop...")

while True:
    log_and_send("⏳ Still running...")
    time.sleep(30)
