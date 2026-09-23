from pathlib import Path
from time import monotonic
from urllib.parse import urlparse
from playwright.sync_api import Error as PlaywrightError
from camoufox import Camoufox
from dotenv import load_dotenv, set_key
import requests
import os

ENV_PATH = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=ENV_PATH)

DIARY_URL = "https://www.myfitnesspal.com/food/diary"
SESSION_COOKIE = "__Secure-next-auth.session-token"
LOGIN_TIMEOUT_SECONDS = 120
REQUIRED_COOKIES = {
    SESSION_COOKIE: "MFP_SESSION_TOKEN",
    "_mfp_session": "MFP_MFP_SESSION",
}


def _build_cookie_header() -> str:
    return (
        f"__Secure-next-auth.session-token={os.getenv('MFP_SESSION_TOKEN')}; "
        f"_mfp_session={os.getenv('MFP_MFP_SESSION')}"
    )

def cookies_still_valid() -> bool:
    """
    Check if the required cookies are still valid by making a request to the MyFitnessPal website.
    Returns True if the cookies are valid, False otherwise.
    """
    session_token = os.getenv("MFP_SESSION_TOKEN")
    mfp_session = os.getenv("MFP_MFP_SESSION")
    if not session_token or not mfp_session:
        return False
    
    response = requests.get("https://www.myfitnesspal.com/food/diary", headers={"Cookie": _build_cookie_header()}, allow_redirects=False, timeout=15)
    return response.status_code == 200

def _save_cookie(env_key: str, value: str):
    set_key(str(ENV_PATH), env_key, value)
    os.environ[env_key] = value
    
def relogin_camoufox():
    print("Opening browser for login (camoufox)...")
    try:
        cookie_map = _capture_cookies_with_browser()
    except PlaywrightError as e:  # closed the window, or the diary never loaded
        print(f"Browser login didn't complete: {e}")
        cookie_map = None

    if cookie_map is None:
        relogin_manual()
        return
    
    missing = [name for name in REQUIRED_COOKIES if name not in cookie_map]

    if missing:
        print(f"Camoufox login didn't produce expected cookies: {missing}.")
        relogin_manual()
        return

    for cookie_name, env_key in REQUIRED_COOKIES.items():
        _save_cookie(env_key, cookie_map[cookie_name])

    if not cookies_still_valid():
        print("Cookies captured but still not authenticating.")
        relogin_manual()
        return

    print("Session refreshed and saved to .env.")

    
def _wait_for_login(page, timeout_s) -> bool:
    """Poll until every required cookie exists, redirecting the browser to the diary if needed."""
    required = set(REQUIRED_COOKIES)
    deadline = monotonic() + timeout_s

    while monotonic() < deadline:
        names = {c["name"] for c in page.context.cookies()}

        if required <= names:
            return True

        # Logged in, but MFP sent us somewhere other than the diary -
        # go there, since that's what sets _mfp_session
        if SESSION_COOKIE in names and urlparse(page.url).path != "/food/diary":
            page.goto(DIARY_URL)

        page.wait_for_timeout(1000)

    return False

def _capture_cookies_with_browser():
    """Returns a {name: value} cookie dict, or None if login didn't complete."""
    with Camoufox(headless=False, geoip=True) as browser:
        page = browser.new_page()
        page.goto(DIARY_URL)

        print(f"Log in in the browser window (waiting up to {LOGIN_TIMEOUT_SECONDS // 60} minutes)...")
        if not _wait_for_login(page, LOGIN_TIMEOUT_SECONDS):
            print("Timed out waiting for login.")
            return None

        page.wait_for_selector("#diary-table", timeout=30_000)
        print("Login detected.")
        return {c["name"]: c["value"] for c in page.context.cookies()}

def relogin_manual():
    """
    Manual login for now, cloudflare stops playwright attempts to capture cookies

    Raises:
        RuntimeError: cookies not copied correctly or still not authenticating
    """
    print("=" * 60)
    print("Session expired or missing.")
    print("1. Log in to https://www.myfitnesspal.com/account/login in your normal browser.")
    print("2. Open DevTools (F12) → Application → Cookies → www.myfitnesspal.com")
    print("3. Copy the two values below when prompted.")
    print("=" * 60)

    _prompt_and_save_cookie("MFP_SESSION_TOKEN", "__Secure-next-auth.session-token")
    _prompt_and_save_cookie("MFP_MFP_SESSION", "_mfp_session")

    if not cookies_still_valid():
        raise RuntimeError("Cookies saved, but still not authenticating. Double-check you copied the values (not names), and that both are pasted correctly.")

    print("Session refreshed and saved to .env.")

def _prompt_and_save_cookie(env_key: str, label: str):
    print(f"\nPaste the value of '{label}' cookie (from DevTools → Application → Cookies):")
    value = input("> ").strip()
    if not value:
        raise RuntimeError(f"No value entered for {label}.")
    _save_cookie(env_key, value)

def ensure_authenticated():
    """
    Ensure that the user is authenticated by checking for the presence of an access token.
    If the access token is not found, raise an exception.
    """
    if not cookies_still_valid():
        relogin_camoufox()
    else:
        print("Cookies are valid. Proceeding with the request.")
        
if __name__ == "__main__":
    ensure_authenticated()