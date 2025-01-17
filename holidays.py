import datetime
import itertools
from astropy.time import Time
from astropy import units as u
import re
from io import StringIO

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup, Tag
from population import subject_names
from utils import YEAR_START, YEAR_AFTER_FINISH

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
                unclear.append([colored, row])
                # print("is contained")
            else:
                # print(date_raw)
                day, month = date_raw.split()
                month_as_num = MONTHS.index(month)
                established = holiday_established_date(colored[-1])
                # print(date_raw, established)
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
    # print(df_holidays)
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


def uraza_bayram():
    return ["19.08.2012", "08.08.2013", "29.07.2014", "18.07.2015", "06.07.2016", "25.06.2017",
            "15.06.2018", "04.06.2019", "24.05.2020", "13.05.2021", "03.05.2022", "22.04.2023"]


def eid_al_adha_date():
    """
    Рассчитывает дату Курбан-байрама для заданного года по григорианскому календарю.

    Args:
    year: Год, для которого нужно рассчитать дату.

    Returns:
    Строка с датой Курбан-байрама в формате "YYYY-MM-DD".
    """
    for year in range(YEAR_START, YEAR_AFTER_FINISH):
        date = Time(f'{year}-07-01') + (10 + int((11 * (year % 19) + 1) / 30)) * u.day
        print(date.strftime("%d.%m.%Y"))


def text_to_month_dates(sources: list):
    dates = []
    for source in sources:
        day, month, year = source.split()
        old = formatted_date(int(day), MONTHS.index(month), int(year))
        actual = datetime.datetime.strptime(old, "%d.%m.%Y") + datetime.timedelta(days=1)
        dates.append(actual.strftime("%d.%m.%Y"))
    # print(dates)
    return dates


def kurban_bayram():
    sources = [
        "25 октября 2012",
        "14 октября 2013",
        "4 октября 2014",
        "23 сентября 2015",
        "12 сентября 2016",
        "31 августа 2017",
        "20 августа 2018",
        "10 августа 2019",
        "30 июля 2020",
        "19 июля 2021",
        "8 июля 2022",
        "27 июня 2023"
    ]
    return text_to_month_dates(sources)


def chaga_bayram():
    # в респ Алтай с 2012
    sources = [
        "26 февраля 2012",
        "17 февраля 2013",
        "7 февраля 2014",
        "27 февраля 2015",
        "19 февраля 2016",
        "10 февраля 2017",
        "17 февраля 2018",
        "9 февраля 2019",
        "24 февраля 2020",
        "14 февраля 2021",
        "6 февраля 2022",
        "23 февраля 2023"
    ]
    return text_to_month_dates(sources)


def sagaalgan():
    soup = BeautifulSoup(
        requests.get("https://ru.wikipedia.org/wiki/%D0%A6%D0%B0%D0%B3%D0%B0%D0%BD_%D0%A1%D0%B0%D1%80").text,
        "html.parser"
    )
    tds = soup.select("table.standard td")
    dates = []
    since = datetime.datetime.strptime("01.01.2012", "%d.%m.%Y")
    until = datetime.datetime.strptime("31.12.2023", "%d.%m.%Y")
    for td in tds:
        # print(td.text, len(td.text))
        actual = datetime.datetime.strptime(td.text.strip(), "%d.%m.%y") + datetime.timedelta(days=1)
        if since <= actual <= until:
            dates.append(actual.strftime("%d.%m.%Y"))
    # print(dates)
    return dates


def surharban():
    sources = [
        "30 июня 2012",
        "28 июня 2013",
        "27 июня 2014",
        "27 июня 2015",
        "24 июня 2016",
        "6 июля 2017",
        "23 июня 2018",
        "29 июня 2019",
        "27 июня 2020",
        "22 июня 2021",
        "1 июля 2022",
        "29 июня 2023"
    ]
    return text_to_month_dates(sources)

def buddha_birthday():
    sources = [
        "4 июня 2012",
        "25 мая 2013",
        "14 июня 2014",
        "2 июня 2015",
        "21 мая 2016",
        "9 июня 2017",
        "29 мая 2018",
        "17 июня 2019",
        "5 июня 2020",
        "26 мая 2021",
        "14 июня 2022",
        "4 июня 2023"
    ]
    return text_to_month_dates(sources)


def zul():
    sources = [
        "8 декабря 2012",
        "27 декабря 2013",
        "16 декабря 2014",
        "5 декабря 2015",
        "23 декабря 2016",
        "12 декабря 2017",
        "2 декабря 2018",
        "21 декабря 2019",
        "10 декабря 2020",
        "29 декабря 2021",
        "18 декабря 2022",
        "7 декабря 2023"
    ]
    return text_to_month_dates(sources)


def shift_dates(dates: list, days=1):
    shifted = []
    for date in dates:
        shifted.append(
            (datetime.datetime.strptime(date, "%d.%m.%Y") + datetime.timedelta(days=days)).strftime("%d.%m.%Y")
        )
    return shifted


def after_easter():
    sources = [
        "12 апреля 2015",
        "1 мая 2016",
        "16 апреля 2017",
        "8 апреля 2018",
        "28 апреля 2019",
        "19 апреля 2020",
        "2 мая 2021",
        "24 апреля 2022",
        "16 апреля 2023"
    ]
    old = text_to_month_dates(sources)
    return shift_dates(old)


def holy_trinity():
    sources = [
        "3 июня 2012",
        "23 июня 2013",
        "8 июня 2014",
        "31 мая 2015",
        "19 июня 2016",
        "4 июня 2017",
        "27 мая 2018",
        "16 июня 2019",
        "7 июня 2020",
        "20 июня 2021",
        "12 июня 2022",
        "4 июня 2023"
    ]
    return shift_dates(text_to_month_dates(sources))


def all_souls_day():
    soup = BeautifulSoup(
        requests.get("https://docs.cntd.ru/document/424090174").text,
        "html.parser"
    )
    table = soup.select("#P0013")
    df = pd.concat(pd.read_html(StringIO(str(table[0]))))[2:].reset_index(drop=True)
    # print(df)
    dates = []
    for index, row in df.iterrows():
        year = int(row[0])
        if YEAR_START <= year < YEAR_AFTER_FINISH:
            day, month = row[1].split()
            dates.append(formatted_date(int(day), MONTHS.index(month), year))
    # print(dates)
    return dates


def shagaa():
    sources = [
        "22 февраля 2012",
        "9 февраля 2013",
        "31 января 2014",
        "9 февраля 2016",
        "27 февраля 2017",
        "16 февраля 2018",
        "5 февраля 2019",
        "24 февраля 2020",
        "12 февраля 2021",
        "1 февраля 2022",
        "21 февраля 2023"
    ]
    return text_to_month_dates(sources)


def naadym():
    sources = [
        "16 августа 2012",
        "12 июля 2013",
        "8 сентября 2014",
        "24 июля 2015",
        "16 августа 2016",
        "14 августа 2017",
        "16 июля 2018",
        "17 июля 2018",
        "15 июля 2019",
        "16 июля 2019",
        "3 сентября 2020",
        "24 сентября 2021",
        "16 августа 2022",
        "14 августа 2023"
    ]
    return text_to_month_dates(sources)


def holiday_lists():
    return {
        "Радоница": radonitsa(),
        "Ураза-Байрам": uraza_bayram(),
        "Курбан-Байрам": kurban_bayram(),
        "Чага-Байрам": chaga_bayram(),
        "Сагаалган": sagaalgan(),
        "Ид аль-Фитр": uraza_bayram(),
        "Ид аль-Адха": kurban_bayram(),
        "Сур-Харбан": surharban(),
        "Цаган Сар": sagaalgan(),
        "День рождения Будды Шакьямуни": buddha_birthday(),
        "Зул": zul(),
        "Курбан Байрам": kurban_bayram(),
        "Светлое Христово Воскресение": after_easter(),
        "Ораза-Байрам": uraza_bayram(),
        "День Святой Троицы": holy_trinity(),
        "Единый день поминовения усопших": all_souls_day(),
        "Шагаа": shagaa(),
        "Наадым": naadym(),
    }


def plain_days_for_regions():
    regions = pd.DataFrame(subject_names())
    print(regions)
    all_time = process_years()
    print(all_time)
    result = regions.merge(all_time, how="cross").reset_index(drop=True)
    return result


def replace_wrong_region_names_for_holidays(df: pd.DataFrame):
    return (
        df
        .replace("Алтай", "Республика Алтай", regex=True)
        .replace("Башкортостан", "Республика Башкортостан", regex=True)
        .replace("Бурятия", "Республика Бурятия", regex=True)
        .replace("Дагестан", "Республика Дагестан", regex=True)
        .replace("Ингушетия", "Республика Ингушетия", regex=True)
        .replace("Кабардино-Балкария", "Кабардино-Балкарская Республика", regex=True)
        .replace("Калмыкия", "Республика Калмыкия", regex=True)
        .replace("Карачаево-Черкессия", "Карачаево-Черкесская Республика", regex=True)
        .replace("Крым", "Республика Крым", regex=True)
        .replace("Татарстан", "Республика Татарстан", regex=True)
        .replace("Тыва", "Республика Тыва", regex=True)
        .replace("Чечня", "Чеченская Республика", regex=True)
        .replace("Коми", "Республика Коми", regex=True)
        .replace("Севастополь", "г. Севастополь", regex=True)
        .replace("Удмуртия", "Республика Удмуртия", regex=True)
        .replace("Чувашия", "Чувашская Республика", regex=True)
        .replace("Якутия", "Республика Саха (Якутия)", regex=True)
    )


def fill_movable_holiday():
    df_holidays, movable = region_holidays()
    # print(df_holidays)
    local_dates = holiday_lists()
    additional = []
    for colored, row in movable:
        established = holiday_established_date(colored[-1])
        if established is None:
            established = "01.01.2001"
        since = datetime.datetime.strptime(established, "%d.%m.%Y")
        # print(colored[1].text.strip(), since.strftime("%d.%m.%Y"))
        for name, dates in local_dates.items():
            if name in colored[1].text:
                for date in dates:
                    comparable = datetime.datetime.strptime(date, "%d.%m.%Y")
                    if comparable >= since:
                        additional.append([row["Субъект РФ"], date])
                        # print(row["Субъект РФ"].strip(), date)
        # print("----")
    print(additional)
    df_additional = pd.DataFrame.from_records(np.array(additional))
    df_additional = replace_wrong_region_names_for_holidays(df_additional)
    df_holidays = replace_wrong_region_names_for_holidays(df_holidays)
    # names = df_holidays.iloc[:, 0].unique().tolist()
    # regions = subject_names()
    # diff = [name for name in names if name not in regions]
    # print(diff)
    # print(df_holidays)
    # print(df_additional)
    return pd.concat([df_holidays, df_additional])


def updated_holidays():
    plain = plain_days_for_regions()
    plain.columns = ["subject", "date", "work/holiday"]
    updates = fill_movable_holiday()
    updates.columns = ["subject", "date"]
    updates["work/holiday"] = 1
    updates = updates.set_index(["subject", "date"])
    plain = plain.set_index(["subject", "date"])
    print(plain)
    print(updates)
    for index, row in updates.iterrows():
        # print(index)
        plain.loc[index] = 1
    return plain


def holidays_for_regions():
    regions = subject_names()
