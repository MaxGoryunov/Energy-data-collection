from functools import reduce

import pandas as pd
from utils import subject_names, yearly_population, test_non_found_regions, format_search_data, remaining_regions, \
    fill_remaining_yearly_population

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

if __name__ == '__main__':
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
        yearly.columns = ["Субъект РФ",  year]
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
