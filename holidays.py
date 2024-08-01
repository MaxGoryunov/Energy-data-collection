import datetime
import itertools
import re
from io import StringIO

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup, Tag
from population import subject_names


YEAR_START = 2012
YEAR_AFTER_FINISH = 2024
MONTHS = [
    "ZERO", "января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
    "декабря"
]


def month_tables(year):
    url = f"https://www.consultant.ru/law/ref/calendar/proizvodstvennye/{year}/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    return soup.find_all("table", class_="cal")


def formatted_date(day: int, month: int, year: int):
    date = ""
    if day < 10:
        date += "0"
    date += f"{day}."
    if month < 10:
        date += "0"
    date += f"{month}.{year}"
    return date


def formatted_date_from_sections(sections: list):
    day, month, year = sections
    return formatted_date(int(day), int(month), int(year))


def process_months(months: list[Tag], year):
    order = 1
    holidays = []
    for month in months:
        name = month.find("th", class_="month")
        days = month.select("td:not(.inactively)")
        for day in days:
            dd = int(day.text.replace("*", ""))
            date = formatted_date(dd, order, year)
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
        if year == 2020:
            months = month_tables(f"{year}b")
        else:
            months = month_tables(year)
        df = process_months(months, year)
        dfs.append(df)
        print(year, len(df))
    return pd.concat(dfs, ignore_index=True)
    # print(blueprint)


def numbered_sections(td: Tag):
    regexes = [
        r"Установлен .*? (\d{1,2})\.(\d{1,2})\.(\d{4})",
        r"Учрежден .*? (\d{1,2})\.(\d{1,2})\.(\d{4})",
        r"Введен .*? (\d{1,2})\.(\d{1,2})\.(\d{4})",
        r"^(\d{1,2})\.(\d{1,2})\.(\d{4})",
    ]
    content = []
    for reg in regexes:
        content = re.findall(reg, td.text)
        if content:
            return formatted_date_from_sections(list(content[0]))
    return ""



def numbered_and_wordly_sections(td: Tag):
    regexes = [
        r"Установлен .*? (\d{1,2}) (.+) (\d{1,4})",
        r"Учрежден .*? (\d{1,2}) (.+) (\d{1,4})",
        r"Введен .*? (\d{1,2}) (.+) (\d{1,4})",
        r"^(\d{1,2}) ([^\s]*?) (\d{4})"
    ]
    for reg in regexes:
        content = re.findall(reg, td.text)
        if content:
            sections = list(content[0])
            sections[1] = str(MONTHS.index(sections[1]))
            return formatted_date_from_sections(sections)
    return ""


def only_year_sections(td: Tag):
    regexes = [
        r"Отмечается с (\d{4})",
        r"\d{4}"
    ]
    for reg in regexes:
        content = re.findall(reg, td.text)
        if content:
            return f"01.01.{content[0]}"


def holiday_established_date(td: Tag):
    since = numbered_sections(td)
    if not since:
        since = numbered_and_wordly_sections(td)
    if not since:
        since = only_year_sections(td)
    return since


def region_holidays():
    # return {
    #     "Республика Адыгея": {
    #         "Радоница": ["11.05.2021", "03.05.2022", "25.04.2023"],
    #         "Ураза-байрам": ["19.08.2012", "08.08.2013", "29.07.2014", "18.07.2015", "06.07.2016", "25.06.2017",
    #                          "15.06.2018", "04.06.2019", "24.05.2020", "13.05.2021", "03.05.2022", "22.04.2023"],
    #         "Курбан-байрам": ["20.07.2021", "09.07.2022", "28.06.2023"],
    #         "День образования Республики Адыгея": [
    #             f"05.10.{year}" for year in range(YEAR_START, YEAR_AFTER_FINISH)
    #         ]
    #     },
    #     "День образования Республики Адыгея": {
    #
    #     }
    # }
    url = "https://ru.wikipedia.org/wiki/%D0%9F%D1%80%D0%B0%D0%B7%D0%B4%D0%BD%D0%B8%D0%BA%D0%B8_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    tables = soup.find_all("table", class_="wikitable")
    table = tables[-1]
    df = pd.concat(pd.read_html(StringIO(str(table))))
    # print(df)
    lines = table.find_all("tr")
    unclear = []
    holidays = []
    for index, row in df.iterrows():
        line = lines[index + 1]
        colored = line.find_all("td", {"bgcolor": "#FFC0CB"})
        if len(colored) != 0:
            date_raw = colored[0].text
            # print(date_raw)
            if "Переходящий праздник" in date_raw:
                unclear.append([line, row])
                # print("is contained")
            else:
                # print(date_raw)
                day, month = date_raw.split()
                month_as_num = MONTHS.index(month)
                established = holiday_established_date(colored[-1])
                print(date_raw, established)
                since = datetime.datetime.strptime(
                    established,
                    "%d.%m.%Y"
                )
                for year in range(YEAR_START, YEAR_AFTER_FINISH):
                    date = datetime.datetime.strptime(
                        formatted_date(int(day), month_as_num, year),
                        "%d.%m.%Y"
                    )
                    if date > since:
                        holidays.append([row["Субъект РФ"], date.strftime("%d.%m.%Y")])
    df_holidays = pd.DataFrame.from_records(np.array(holidays))
    print(df_holidays)
    return df_holidays, unclear


def radonitsa():
    source = """Радоница в 2012 году — 24 апреля;
        Радоница в 2013 году — 14 мая;
        Радоница в 2014 году — 29 апреля;
        Радоница в 2015 году — 21 апреля;
        Радоница в 2016 году — 10 мая;
        Радоница в 2017 году — 25 апреля;
        Радоница в 2018 году — 17 апреля;
        Радоница в 2019 году — 7 мая;
        Радоница в 2020 году — 28 апреля;
        Радоница в 2021 году — 11 мая;
        Радоница в 2022 году — 3 мая;
        Радоница в 2023 году — 25 апреля"""
    lines = source.split(";")
    dates = []
    for line in lines:
        _, _, year, _, _, day, month = line.split()
        month_as_num = MONTHS.index(month)
        date = formatted_date(int(day), month_as_num, int(year))
        dates.append(date)
    return dates





def holidays_for_regions():
    regions = subject_names()

