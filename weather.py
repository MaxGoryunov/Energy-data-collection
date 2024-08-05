from io import StringIO
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import difflib
import openmeteo_requests
import requests_cache
from retry_requests import retry
from utils import YEAR_START, YEAR_AFTER_FINISH
from transliterate import translit
from selenium.webdriver.support.select import Select

from population import subject_names


MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь",
          "Ноябрь", "Декабрь"]


def weather_region_names():
    driver = Chrome()
    driver.get("https://www.gismeteo.ru/diary/4079/")
    options = driver.find_elements(By.CSS_SELECTOR, "#sd_distr>option")
    names = []
    for option in options:
        names.append(option.text)
    return names[2:]


def region_centres_russian() -> dict:
    soup = BeautifulSoup(
        requests.get("https://ru.wikipedia.org/wiki/%D0%90%D0%B4%D0%BC%D0%B8%D0%BD%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%82%D0%B8%D0%B2%D0%BD%D1%8B%D0%B5_%D1%86%D0%B5%D0%BD%D1%82%D1%80%D1%8B_%D1%81%D1%83%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%BE%D0%B9_%D0%A4%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8").text,
        "html.parser"
    )
    table = soup.select("table.standard")[0]
    df = pd.concat(pd.read_html(StringIO(str(table)))). \
        loc[:, ["Субъект Российской Федерации", "Административный центр"]].dropna().reset_index(drop=True). \
        replace("\[1\]", "", regex=True)
    df.columns = ["region", "capital"]
    pairs = {}
    regions = weather_region_names()
    for index, row in df.iterrows():
        region = row["region"]
        matches = difflib.get_close_matches(region, regions, n=87, cutoff=0.4)
        if matches:
            if region in ["Москва", "Санкт-Петербург", "Севастополь"]:
                print("Special city")
                pairs[f"{region} (город федерального значения)"] = row["capital"]
            else:
                print(len(matches), region, matches[:3])
                pairs[matches[0]] = row["capital"]
        else:
            print(region)
    # print(df)
    print(pairs)
    return pairs


def find_similar_centre(centre: str, driver: Chrome):
    cities = driver.find_elements(By.CSS_SELECTOR, "#sd_city>option")
    # print(cities)
    txts = []
    for city in cities:
        txts.append(city.text)
    print(txts)
    return difflib.get_close_matches(centre, txts, n=1)[0]


def weather_data():
    pairs = region_centres_russian()
    driver = Chrome()
    driver.get("https://www.gismeteo.ru/diary/4079/")
    region_select = Select(driver.find_element(By.ID, "sd_distr"))
    centre_select = Select(driver.find_element(By.ID, "sd_city"))
    month_select = Select(driver.find_element(By.ID, "date_Month"))
    year_select = Select(driver.find_element(By.ID, "date_Year"))
    submit = driver.find_element(By.ID, "selector_go_btn")
    for region, centre in pairs.items():
        region_select.select_by_visible_text(region)
        sleep(0.5)
        closest = find_similar_centre(centre, driver)
        centre_select.select_by_visible_text(closest)
        print(region, centre, closest)
        for year in range(YEAR_START, YEAR_AFTER_FINISH):
            for month in MONTHS:
                print(region, centre, year, month)
                month_select.select_by_visible_text(month)
                year_select.select_by_visible_text(str(year))
                submit.click()
                table = driver.find_element(By.CSS_SELECTOR, "#data_block>table")
                df = pd.read_html(StringIO(table.get_attribute("outerHTML")))[0]
                print(df)

                return


def region_to_centre():
    soup = BeautifulSoup(
        requests.get("https://ru.wikipedia.org/wiki/%D0%90%D0%B4%D0%BC%D0%B8%D0%BD%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%82%D0%B8%D0%B2%D0%BD%D1%8B%D0%B5_%D1%86%D0%B5%D0%BD%D1%82%D1%80%D1%8B_%D1%81%D1%83%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%BE%D0%B9_%D0%A4%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8").text,
        "html.parser"
    )
    table = soup.select("table.standard")[0]
    df = pd.read_html(StringIO(str(table)))[0].loc[:, ["Субъект Российской Федерации", "Административный центр"]] \
        .rename(
        columns={"Субъект Российской Федерации": "region", "Административный центр": "capital"}
        ) \
        .set_index("region") \
        .dropna()
    pairs = {}
    for index, row in df.iterrows():
        pairs[index] = row["capital"]
    print(pairs)
    return pairs





def open_meteo_data():
    coords = pd.read_csv("coordinates.csv")
    # print(coords)
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    url = "https://archive-api.open-meteo.com/v1/archive"
    for index, row in coords.iterrows():
        city, lat, lon = row
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": "2012-01-01",
            "end_date": "2023-12-31",
            "hourly": ["temperature_2m", "relative_humidity_2m"]
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ), "temperature_2m": hourly_temperature_2m, "relative_humidity_2m": hourly_relative_humidity_2m}

        df = pd.DataFrame(data=hourly_data)
        df[["date", "time"]] = df["date"].dt.strftime("%Y-%m-%d %H:%M:%S").str.split(" ", expand=True)
        print(df)
        break

