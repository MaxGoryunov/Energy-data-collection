from functools import reduce

import pandas as pd

from holidays import get_month_tables
from population import subject_names, yearly_population, test_non_found_regions, format_search_data, remaining_regions, \
    fill_remaining_yearly_population
from daylight_hours import region_capitals, capitals_coordinates


if __name__ == '__main__':
    get_month_tables(2012)
