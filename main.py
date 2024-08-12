from functools import reduce

import pandas as pd

from aggreg import aggregation_by_year
from holidays import month_tables, process_months, process_years, region_holidays, radonitsa, eid_al_adha_date, \
    kurban_bayram, sagaalgan, all_souls_day, fill_movable_holiday, plain_days_for_regions, updated_holidays
from investment import investment, properly_named_investment
from population import subject_names, yearly_population, test_non_found_regions, format_search_data, remaining_regions, \
    fill_remaining_yearly_population, population_report
from daylight_hours import region_capitals, capitals_coordinates
from unemployment import unemployment_rate, properly_named_unemployment_rate
from vrp import vrp_up_to_2015, vrp_up_to_2022, combined_vrp
from weather import region_centres_russian, weather_region_names, weather_data, open_meteo_data, \
    region_to_centre, centre_to_region_translated

if __name__ == '__main__':
    aggregation_by_year()

