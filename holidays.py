import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

def get_month_tables(year: int):
    url = f"https://www.consultant.ru/law/ref/calendar/proizvodstvennye/{year}/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    months = soup.find_all("table", class_="cal")
    for month in months:
        name = month.find("th", class_="month")
        days = month.find_all("td", class_=["holiday", "weekend", "work"])

        print(name.text, len(days))
