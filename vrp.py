import pandas as pd
import numpy as np
import difflib

from population import subject_names


def vrp_up_to_2015():
    df = pd.read_excel("VRP_s_1998.xlsx", sheet_name="1")
    # df = df.rename(columns={"К содержанию": "region"})
    # print(df)
    df.columns = df.iloc[1]
    df = (df.iloc[3:].rename(columns={np.nan: "region"}))
    df = df[~(df["region"].str.endswith("федеральный округ"))] \
        .reset_index(drop=True).loc[:, ["region", *range(2012, 2016)]]
    # print(df[60:70])
    rewrite = [(20, 22), (61, 64)]
    dropped = [dest for source, dest in rewrite]
    for replaced, replacement in rewrite:
        region = df.loc[replaced, "region"]
        df.loc[replaced, :] = df.loc[replacement, :]
        df.loc[replaced, "region"] = region
    df = df.drop(dropped).reset_index(drop=True)
    # print(df[df["region"]=="Тюменская область"])
    return df


def vrp_up_to_2022():
    df = pd.read_excel("VRP_s_1998.xlsx", sheet_name="2")
    # df = df.rename(columns={"К содержанию": "region"})
    # print(df)
    df.columns = df.iloc[1]
    df = (df.iloc[3:].rename(columns={np.nan: "region"})).dropna()
    # print(df)
    df = df[~(df["region"].str.endswith("федеральный округ"))] \
             .reset_index(drop=True).loc[:, ["region", *range(2016, 2023)]]
    # print(df[60:70])
    rewrite = [(20, 22), (61, 64)]
    dropped = [dest for source, dest in rewrite]
    for replaced, replacement in rewrite:
        region = df.loc[replaced, "region"]
        df.loc[replaced, :] = df.loc[replacement, :]
        df.loc[replaced, "region"] = region
    df = df.drop(dropped).reset_index(drop=True)
    # print(df[df["region"] == "Тюменская область"])
    return df


def check_remaining_regions(df: pd.DataFrame):
    target = subject_names()
    regions = df.loc[:, "region"].tolist()
    for region in regions:
        matches = difflib.get_close_matches(region, target, n=3, cutoff=0.3)
        if region != matches[0]:
            if region == "Удмуртская Республика":
                df.loc[df["region"] == region, "region"] = "Республика Удмуртия"
            else:
                df.loc[df["region"]==region, "region"] = matches[0]
            print(region, matches[0])
    df.loc[df["region"]=="Удмуртская Республика", "region"] = "Республика Удмуртия"


def combined_vrp():
    old: pd.DataFrame = vrp_up_to_2015()
    new: pd.DataFrame = vrp_up_to_2022()
    combined = (old.merge(new, "outer", on=["region"])
                .replace("-Югра", "", regex=True)
                .replace("автономный округ", "АО", regex=True)
                .replace("авт. округ", "АО", regex=True)
                .replace("-Кузбасс", "", regex=True)
                .replace("в т.ч. ", "", regex=True))
    combined.loc[:, "region"] = combined.loc[:, "region"].str.strip()
    print(combined)
    check_remaining_regions(combined)
    combined = combined[["region", *range(2012, 2023)]].reset_index(drop=True)
    print(combined.index.name)
    print(combined.columns)
    renamed = {}
    for year in range(2012, 2023):
        combined.loc[:, year] = 1000000 * combined.loc[:, year]
        renamed[year] = f"01.01.{year}"
    combined = combined.rename(columns=renamed)
    combined = combined.melt(
        id_vars=["region"],
        value_vars=[col for col in combined.columns if col != "region"],
        var_name="date",
        value_name="vrp"
    ).sort_values(by=["region", "date"]).reset_index(drop=True)
    print(combined)
    combined.to_csv("vrp.csv", index=False)
    return combined
