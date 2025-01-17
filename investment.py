import pandas as pd
import numpy as np
import difflib

from population import subject_names


def investment():
    df = pd.read_excel("Invest_SUB.xlsx", sheet_name="Лист1")
    # print(df)
    df.columns = df.iloc[2]
    df = df.rename(columns={np.nan: "region"}).loc[4:, ["region", *range(2012, 2024)]].dropna()
    # print(df)
    # print(df["region"].str.endswith("федеральный округ"))
    df["region"] = df["region"].str.strip()
    df = df[~(df["region"].str.endswith("федеральный округ"))].reset_index(drop=True)
    # print(df)
    # print(len(subject_names()))
    return df


def properly_named_investment():
    df = investment()
    regions = subject_names()
    for index, row in df.iterrows():
        region = row["region"]
        # print(region)
        matches = difflib.get_close_matches(region, regions, n=3, cutoff=0.3)
        if region == matches[0]:
            print(f"Perfect match for {region}")
            continue
        if region == "Удмуртская Республика":
            df.loc[index, "region"] = "Республика Удмуртия"
        else:
            df.loc[index, "region"] = matches[0]
        print(region, matches)
    for year in range(2012, 2024):
        df.loc[:, year] = 1_000_000 * df.loc[:, year]
    df = df.rename(columns={year: f"01.01.{year}" for year in [*range(2012, 2024)]})
    print(df)
    df = df.melt(
        id_vars=["region"],
        value_vars=[col for col in df.columns if col != "region"],
        var_name="date",
        value_name="investment"
    ).sort_values(by=["region", "date"]).reset_index(drop=True)
    print(df)
    df.to_csv("investment.csv", index=False)
