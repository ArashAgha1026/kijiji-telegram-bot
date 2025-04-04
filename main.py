# TEMP TEST: Minimal main.py to confirm what's crashing

print("🚀 Bot is starting up...")

# 1. Try importing Playwright only
try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright imported successfully")
except Exception as e:
    print("❌ Failed to import playwright:", e)
    exit(1)

# 2. Try launching the browser (headless)
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://example.com")
        page.wait_for_timeout(3000)
        print("✅ Successfully loaded example.com")
        browser.close()
except Exception as e:
    print("❌ Failed during browser operation:")
    import traceback
    traceback.print_exc()
    exit(1)

print("✅ Bot ran to the end without crashing")
