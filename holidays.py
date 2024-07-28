import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup, Tag
from population import subject_names


def month_tables(year: int):
    url = f"https://www.consultant.ru/law/ref/calendar/proizvodstvennye/{year}/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    return soup.find_all("table", class_="cal")


def process_months(months: list[Tag], year: int):
    order = 1
    holidays = []
    for month in months:
        name = month.find("th", class_="month")
        days = month.select("td:not(.inactively)")
        for day in days:
            dd = int(day.text.replace("*", ""))
            date = ""
            if dd < 10:
                date += "0"
            date += f"{dd}."
            if order < 10:
                date += "0"
            date += f"{order}.{year}"
            if "weekend" in day["class"] or "holiday" in day["class"]:
                holidays.append([date, 1])
            else:
                holidays.append([date, 0])
            # print(day.text.strip(), day["class"])
        order += 1
        # print(name.text)
    return pd.DataFrame.from_records(np.array(holidays))


def process_years():
    dfs = []
    for year in range(2012, 2024):
        months = month_tables(year)
        df = process_months(months, year)
        dfs.append(df)
        print(year, len(df))
    blueprint = pd.concat(dfs, ignore_index=True)
    print(blueprint)
