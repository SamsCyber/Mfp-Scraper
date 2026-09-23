import csv

def export_to_csv(days: list[dict], start_date: str, end_date: str, output_path: str):
    """
    days: list of dicts like {'protein_g': 199, 'carbs_g': 216, 'fat_g': 43, ...}
    start_date / end_date: 'YYYY-MM-DD' strings, written as a header row.
    """
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([f"{start_date} to {end_date}"])
        writer.writerow(["Date", "Protein (g)", "Carbs (g)", "Fats (g)"])
        for day in days:
            writer.writerow([day["date"], day["protein_g"], day["carbs_g"], day["fat_g"]])

    print(f"Saved to {output_path}")
    print(f"{start_date} to {end_date}")
    print("Date, Protein (g), Carbs (g), Fats (g)")
    for day in days:
        print(f"{day['date']}, {day['protein_g']}, {day['carbs_g']}, {day['fat_g']}")