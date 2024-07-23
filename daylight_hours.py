from io import StringIO

import pandas as pd
import numpy as np
import requests
import wikipedia
import requests
from bs4 import BeautifulSoup


wikipedia.set_lang("ru")


def region_capitals():
    url = "https://ru.wikipedia.org/wiki/%D0%90%D0%B4%D0%BC%D0%B8%D0%BD%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%82%D0%B8%D0%B2%D0%BD%D1%8B%D0%B5_%D1%86%D0%B5%D0%BD%D1%82%D1%80%D1%8B_%D1%81%D1%83%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%BE%D0%B9_%D0%A4%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8"
    page = requests.get(url)
    print(page.status_code)
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find_all("table", class_=["standard", "sortable", "jquery-tablesorter"])
    df = pd.concat(pd.read_html(StringIO(str(table))))["Административный центр"]
    return df



