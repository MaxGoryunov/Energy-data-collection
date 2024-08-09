import difflib

import numpy as np
import pandas as pd

from population import subject_names

START = 2012
AFTER_FINISH = 2024


def unemployment_rate():
    df = pd.read_excel("Trud_3_15-72.xlsx", sheet_name="2")
    df.columns = df.iloc[3]
    df = df.iloc[3:].rename(columns={np.nan: "region"}).dropna()
    df = df[~(df["region"].str.endswith("федеральный округ"))].drop([4]).reset_index(drop=True) \
        .loc[:, ["region", *range(START, AFTER_FINISH)]] \
        .replace("в том числе:", "", regex=True)
    df["region"] = df["region"].str.strip()
    print(df)
    return df


def properly_named_unemployment_rate():
    df = unemployment_rate()
    regions = subject_names()
    for index, row in df.iterrows():
        region = row["region"]
        matches = difflib.get_close_matches(region, regions, n=3, cutoff=0.3)
        if region == matches[0]:
            print(f"Perfect match for {region}")
            continue
        if region == "Удмуртская Республика":
            df.loc[index, "region"] = "Республика Удмуртия"
        else:
            df.loc[index, "region"] = matches[0]
        # print(region, matches)
    print(df)
    df.to_csv("unemployment.csv", index=False)

