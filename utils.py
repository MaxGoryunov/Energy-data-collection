import numpy as np
import pandas as pd


def subject_names(filename: str, sheet: str, col: int = 0):
    unq = np.array(
        pd.read_excel(filename, sheet_name=sheet).iloc[:, col].unique().tolist()
    )
    ind, = np.where(unq == "Субъект РФ")
    return np.strings.strip(
        np.strings.replace(
            np.delete(unq, ind),
            "[*]",
            ""
        )
    )


def format_search_data(df: pd.DataFrame):
    formatted = (
        df.replace(" - город федерального значения", "", regex=True)
        .replace("^г ", "", regex=True)
        .replace("^г.", "", regex=True)
        .replace("Удмуртская Республика", "Республика Удмуртия", regex=True)
        .replace("Севастополь", "г. Севастополь", regex=True)
        .replace("- Кузбасс", "", regex=True)
        .replace("- Югра", "", regex=True)
        .replace("-Югра", "", regex=True)
        .replace("без Ненецкого автономного округа", "", regex=True)
        .replace("без Ненецкого авт. округа", "", regex=True)
        .replace(
            "\(кроме Ханты-Мансийского автономного округа - Югры и Ямало-Ненецкого автономного округа\)",
            "",
            regex=True
        )
        .replace("без автономных округов", "", regex=True)
        .replace("без авт. округов", "", regex=True)
        .replace("автономный округ", "АО", regex=True)
        .replace("авт. округ", "АО", regex=True)
        .replace('^\s+', '', regex=True)
        .replace('\s+$', '', regex=True)
    )
    # formatted.iloc[:, 0].str.strip()
    return formatted


def yearly_population(df, names):
    return df.loc[df.iloc[:, 0].isin(names)]


def remaining_regions(names, yearly):
    source = yearly.iloc[:, 0].tolist()
    remaining = []
    ind = 1
    for name in names:
        if not (name in source) and name != "Субъект РФ":
            remaining.append(name)
    return remaining


def test_non_found_regions(names, yearly):
    print("Test for ", yearly.columns.tolist())
    regions = remaining_regions(names, yearly)
    ind = 1
    for region in regions:
        print(ind, region)
        ind = ind + 1


def fill_remaining_yearly_population(yearly: pd.DataFrame, remaining):
    for region in remaining:
        yearly.loc[yearly.index.max() + 1] = [region, 0]
