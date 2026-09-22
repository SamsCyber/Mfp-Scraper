from macros import fetch_diary_page_html
from camoufox.sync_api import Camoufox

with Camoufox(headless=False, geoip=True) as browser:
    page = browser.new_page()
    page.goto("https://www.myfitnesspal.com/account/login")

    print("Log in manually, then press Enter here once you're on your diary page.")
    input()

    cookies = page.context.cookies()
    browser.close()

cookie_map = {c["name"]: c["value"] for c in cookies}
print(cookie_map.get("__Secure-next-auth.session-token"))
print(cookie_map.get("_mfp_session"))


# html = fetch_diary_page_html("2026-09-21")

# with open("debug_output.html", "w", encoding="utf-8") as f:
#     f.write(html)
    
# print(f"Got {len(html)} characters back.")