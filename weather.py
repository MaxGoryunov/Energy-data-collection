from io import StringIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import difflib

from population import subject_names


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


def weather_data():
    pass
