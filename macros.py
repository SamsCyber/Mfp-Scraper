import os
from inquirer import text
import requests
from bs4 import BeautifulSoup
from auth import ensure_authenticated
from datetime import date, datetime, timedelta

def fetch_diary_page_html(date: str) -> str:
    ensure_authenticated()
    
    cookies = {
        "_mfp_session": os.getenv("MFP_MFP_SESSION"),
        "__Secure-next-auth.session-token": os.getenv("MFP_SESSION_TOKEN")
    }
    
    url = f"https://www.myfitnesspal.com/food/diary?date={date}"
    response = requests.get(url, cookies=cookies)
    return response.text

def parse_macros_from_html(html_content: str) -> dict:
    """
    Parse the HTML content of the diary page to extract total macros (calories, protein, carbs, fat).
    Returns a dictionary with the total values.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    totals_row = soup.find('tr', class_='total')
    
    cells = totals_row.find_all("td")
    
    def clean_number(text: str) -> int:
        return int(text.strip().replace(",", ""))
    
    cells = totals_row.find_all("td")
    # cells[0] = "Totals" label
    # cells[1] = calories
    # cells[2] = carbs (contains macro-value + macro-percentage spans)
    # cells[3] = fat
    # cells[4] = protein
    # cells[5] = sodium
    # cells[6] = sugar
    
    calories = clean_number(cells[1].get_text())
    carbs = clean_number(cells[2].find("span", class_="macro-value").get_text())
    fat = clean_number(cells[3].find("span", class_="macro-value").get_text())
    protein = clean_number(cells[4].find("span", class_="macro-value").get_text())
    return {"calories": calories, "carbs_g": carbs, "fat_g": fat, "protein_g": protein}


def get_macros_for_range(date_start: str, date_end: str) -> dict:
    """
    Fetches the diary page HTML for the specified date range and extracts the total macros.
    Returns a dictionary with the total calories, protein, carbs, and fat.
    """
    startDate = parse_date(date_start)
    endDate = parse_date(date_end)
    
    if endDate - startDate > timedelta(days=7):
        raise ValueError("Risky request: The date range exceeds 7 days. Please use a smaller range.")
        
    datetime_range = [startDate + timedelta(days=i) for i in range((endDate - startDate).days + 1)] 
    results = []
    
    for day in datetime_range:
        html_content = fetch_diary_page_html(day.strftime("%Y-%m-%d"))
        debug_file_path = f"debug_output.html"
        with open(debug_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        results.append(parse_macros_from_html(html_content))
    
    return {"start_date": date_start, "end_date": date_end, "results": results}

def parse_date(date_str: str) -> date:
    """
    Parse a date string in the format 'YYYY-MM-DD' and return a date object.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Please use 'YYYY-MM-DD'.")