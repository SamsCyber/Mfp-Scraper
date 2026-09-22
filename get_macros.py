from datetime import date, timedelta
from macros import get_macros_for_range
from export import export_to_csv

def get_last_week_range():
    today = date.today()
    end = today
    start = end - timedelta(days=6)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

if __name__ == "__main__":
    start_str, end_str = get_last_week_range()
    result = get_macros_for_range(start_str, end_str)
    export_to_csv(result["results"], result["start_date"], result["end_date"], "week_macros.csv")