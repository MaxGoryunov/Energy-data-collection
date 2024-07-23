from io import StringIO

import pandas as pd
import numpy as np
import requests
import wikipedia
import requests
from bs4 import BeautifulSoup


def region_capitals():
    url = "https://en.wikipedia.org/wiki/Federal_subjects_of_Russia"
    page = requests.get(url)
    print(page.status_code)
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all("table", class_=["wikitable", "sortable", "jquery-tablesorter"])
    df = pd.concat(pd.read_html(StringIO(str(table[2]))))
    df: pd.DataFrame = df.iloc[:, df.columns.get_level_values(1) == "Capital/ Administrative centre[a]"]
    df = (
        df.replace("\[d\]", "", regex=True)
        .replace("^.* \(de facto\) ", "", regex=True)
        .replace(" \(claimed\)", "", regex=True)
        .replace(" \(Largest.*$", "", regex=True)
    )
    df.columns = ["Capital"]
    print(df)
    # df = df["Административный центр"].dropna().reset_index(drop=True)
    return df


def capitals_coordinates(capitals: pd.DataFrame):
    for index, capital in capitals.items():
        page = wikipedia.page(capital)
        soup = BeautifulSoup(page.html(), "html.parser")
        coordinates = soup.find("span", class_="geo-inline").text
        print(page.title, coordinates)
