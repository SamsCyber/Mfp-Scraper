Rather than grab macros from MyFitnessPal app manually in 1 minute, why not spend hours making a script to do the same thing! (FOR PERSONAL USE)

# MFP Macro Scraper

Pulls daily macro totals (protein, carbs, fat) from your MyFitnessPal food diary prior 7 days, exports into a small csv convenient for my use case.

## Setup

**1. Clone the repo and move into it**
```powershell
cd path\to\Mfp-Scraper
```

**2. Create and activate a virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
If PowerShell blocks the activation script, run this once:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**3. Install dependencies**
```powershell
pip install -r requirements.txt
```

**4. Install camoufox's browser binary** (one-time, needed for the login flow)
```powershell
python -m camoufox fetch
```

**5. Set up your `.env` file** <br>
Leave the values blank — the script will prompt you to log in and fill them in automatically on first run.

## Usage

**Run it directly:**
```powershell
python get_macros.py
```

**Or double-click `getMacros.bat`** for a one-click run (handles the venv activation for you, works from any location).

On first run, or whenever your session has expired, a browser window will open for you to log in to MyFitnessPal manually. Once logged in, confirm in the terminal, and your session cookies are saved to `.env` automatically for next time.

By default, it pulls the last 7 days and writes `week_macros.csv` in the project folder, with a printout in the terminal too.

## Project structure

| File | Purpose |
|---|---|
| `auth.py` | Handles login/session validity, refreshes cookies (via camoufox, with a manual fallback) |
| `macros.py` | Fetches diary pages and parses out the macro totals |
| `export.py` | Writes results to CSV |
| `get_macros.py` | Ties it all together — the script you actually run |
| `run_macros.bat` | One-click launcher |
| `requirements.txt` | Python package dependencies |

## Notes

- Cookies are stored locally in `.env`.
- If MyFitnessPal changes its page structure, the parser in `macros.py` may need updating — check `parse_macros_from_html` first if numbers stop coming through correctly.
