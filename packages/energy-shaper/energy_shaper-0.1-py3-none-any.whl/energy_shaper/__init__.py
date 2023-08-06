"""
    energy_shaper
    ~~~~~
    Given energy readings, split and group into given energy load shapes/profiles
"""

from energy_shaper.models import Reading, DaySummary

from energy_shaper.splitter import split_into_intervals
from energy_shaper.splitter import split_into_daily_intervals
from energy_shaper.splitter import split_into_profiled_intervals

from energy_shaper.demand_periods import in_peak_day, in_peak_time
from energy_shaper.demand_periods import in_peak_period

from energy_shaper.grouper import get_group_end
from energy_shaper.grouper import group_into_profiled_intervals
from energy_shaper.grouper import group_into_daily_summary