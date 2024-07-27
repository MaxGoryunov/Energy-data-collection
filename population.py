import numpy as np
import pandas as pd
from functools import reduce


years = {
    "01.01.2012": ("Tabl-03-12.xls", "Табл. 3", 1000, 4),
    "01.01.2013": ("Tabl-03-13.xls", "Табл. 3", 1000, 1),
    "01.01.2014": ("Tabl-03-14.xls", "Табл. 3", 1000, 1),
    "01.01.2015": ("Tabl-03-15.xls", "Табл. 3", 1000, 1),
    "01.01.2016": ("Tabl-03-16.xls", "Табл. 3", 1000, 1),
    "01.01.2017": ("Tabl-03-17.xls", "Табл. 3", 1000, 1),
    "01.01.2018": ("Tabl-01-18.xls", "Табл. 1", 1, 1),
    "01.01.2019": ("Tabl-01-19.xls", "Табл. 1", 1, 1),
    "01.01.2020": ("Tabl-01-20.xls", "Табл. 1", 1, 1),
    "01.01.2021": ("Tabl-01-21.xls", "Табл. 1", 1, 1),
    "01.01.2022": ("Chisl_nasel_RF_MO_01-01-2022.xlsx", "Таб_1", 1, 0),
    "01.01.2023": ("BUL_MO_2023.xlsx", "Таб_1", 1, 0)
}


def subject_names(filename: str, sheet: str, col: int = 0):
    print(type(pd.read_excel(filename, sheet_name=sheet).iloc[:, col].unique()))
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


def population_report():
    names = subject_names("Сбор данных.xlsx", "Год")
    total = []
    for year in years:
        # if year != "01.01.2018":
        #     continue
        print(year)
        file, sheet, count_in, popul_column = years[year]
        df = pd.read_excel(file, sheet_name=sheet)
        formatted = format_search_data(df)
        yearly = yearly_population(formatted, names)
        if 'Содержание' in yearly.columns:
            yearly = yearly.iloc[:, [yearly.columns.get_loc('Содержание'), 1]].reset_index(drop=True)
            # print(yearly[0:10])
            # yearly.rename(
            #     columns={
            #         "Содержание": "Субъект РФ",
            #         popul_column: "Население"
            #     },
            #     inplace=True
            # )
        else:
            yearly = yearly.iloc[:, [0, popul_column]].reset_index(drop=True)
            # yearly.rename(
            #     columns={
            #         0: "Субъект РФ",
            #         popul_column: "Население"
            #     },
            #     inplace=True
            # )
        yearly.columns = ["Субъект РФ", year]
        yearly = yearly.sort_values(by=["Субъект РФ"]).reset_index(drop=True)
        print(yearly["Субъект РФ"].tolist())
        yearly[year] = yearly[year].apply(lambda val: val * count_in)
        test_non_found_regions(names, yearly)
        remaining = remaining_regions(names, yearly)
        print("names = ", len(names), " names - remaining = ", len(names) - len(remaining),
              " found = ", len(yearly["Субъект РФ"]))
        fill_remaining_yearly_population(yearly, remaining)
        # print(yearly[0:10])
        total.append(yearly)
        # print(yearly.columns)
    merged = reduce(lambda left, right: pd.merge(left, right, on=["Субъект РФ"], how="outer"), total)
    # merged =
    print(merged)
    melted = merged.melt(
        id_vars=["Субъект РФ"],
        value_vars=[col for col in merged.columns if col != "Субъект РФ"],
        var_name="Дата",
        value_name="Численность населения"
    ).sort_values(by=["Субъект РФ", "Дата"]).reset_index(drop=True)
    print(melted)
