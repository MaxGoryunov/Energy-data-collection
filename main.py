from functools import reduce

import pandas as pd
from population import subject_names, yearly_population, test_non_found_regions, format_search_data, remaining_regions, \
    fill_remaining_yearly_population
from daylight_hours import region_capitals, capitals_coordinates


if __name__ == '__main__':
    caps = region_capitals()
    print(type(caps))
    # capitals_coordinates(caps)
