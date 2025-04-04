import os
import time
import requests

print("🚀 Bot starting")

try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": "🔄 Bot has entered the main loop!"}
    )
except Exception as e:
    print("❌ Failed to send message:", e)
    exit(1)

print("⚙️ Entering loop...")

while True:
    print("⏳ Still running...")
    time.sleep(30)
