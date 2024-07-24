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
        df.replace("\[.\]", "", regex=True)
        .replace("^.* \(de facto\) ", "", regex=True)
        .replace(" \(claimed\)", "", regex=True)
        .replace(" \(Largest.*$", "", regex=True)
        .replace("Largest city: ", "", regex=True)
    )
    df.columns = ["Capital"]
    # print(df)
    # df = df["Административный центр"].dropna().reset_index(drop=True)
    return df


def capitals_coordinates(capitals: pd.DataFrame):
    rows = []
    remaining = []
    for index, row in capitals.iterrows():
        page = requests.get(f"https://en.wikipedia.org/wiki/{row['Capital']}")
        print(row["Capital"], page.status_code)
        soup = BeautifulSoup(page.text, "html.parser")
        coordinates = soup.find("span", class_="geo-inline")
        if coordinates is None:
            print(f"No coordinates for {row['Capital']}, search in Russia")
            page = requests.get(f"https://en.wikipedia.org/wiki/{row['Capital']},_Russia")
            soup = BeautifulSoup(page.text, "html.parser")
            coordinates = soup.find("span", class_="geo-inline")
            if coordinates is None:
                print(f"No coordinates at all for {row['Capital']}")
                remaining.append(row["Capital"])
                continue
        lat, lon = coordinates.text.split("/")[-1].split(";")
        lat = lat.strip()
        lon = lon.strip()
        rows.append([row["Capital"], lat, lon])
        # print(lat, lon)
    df = pd.DataFrame.from_records(np.array(rows))
    # print(df)
    other = pd.DataFrame([
        ["Kirov", 58.6, 49.683],
        ["Kurgan", 55.4667, 65.35],
        ["Anadyr", 64.7333, 177.5167]
    ])
    full = df._append(other)
    full.to_csv("daylight.csv", index=False)
    print(full)
    print(remaining)
