from functools import reduce

import pandas as pd
import numpy as np


def aggregation_by_year():
    vrp = pd.read_csv("vrp.csv")
    population = pd.read_csv("population.csv")
    unemployment = pd.read_csv("unemployment.csv")
    investment = pd.read_csv("investment.csv")
    dfs = [vrp, population, unemployment, investment]
    merged = reduce(lambda left, right: pd.merge(left, right, on=["region", "date"], how="outer"), dfs)
    print(merged)
    return merged



