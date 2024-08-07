import pandas as pd
import numpy as np


def vrp_up_to_2015():
    years = [2012, 2013, 2014, 2015]
    df = pd.read_excel("VRP_s_1998.xlsx", sheet_name="1")
    # df = df.rename(columns={"К содержанию": "region"})
    # print(df)
    df.columns = df.iloc[1]
    df = (df.iloc[3:].rename(columns={np.nan: "region"}))
    df = df[~(df["region"].str.endswith("федеральный округ"))] \
        .reset_index(drop=True).loc[:, ["region", 2012, 2013, 2014, 2015]]
    print(df[60:70])
    rewrite = [(20, 22), (61, 64)]
    dropped = [dest for source, dest in rewrite]
    for replaced, replacement in rewrite:
        region = df.loc[replaced, "region"]
        df.loc[replaced, :] = df.loc[replacement, :]
        df.loc[replaced, "region"] = region
    df = df.drop(dropped).reset_index(drop=True)
    print(df[df["region"]=="Тюменская область"])
    return df

