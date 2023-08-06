"""
    energy_shaper.demand_periods
    ~~~~~
    Determine demand period for time of day tariffs
"""

import logging
from datetime import datetime, time
from typing import List


def in_peak_period(billing_time: datetime,
                   peak_months: List[int] = [12, 1, 2],
                   peak_days: List[int] = [0, 1, 2, 3, 4, 5, 6],
                   peak_start: time = time(15, 0, 0),
                   peak_end: time = time(21, 30, 0),
                   ) -> bool:
    """ Calculate if billing period falls on a peak day
        :param billing_time: The datetime to check (period ending)
        :param peak_months: List of months that peak applies
        :param peak_days: List of days of week that peak applies
                          (where 0 is Sunday and 6 is Saturday)
        :param peak_start: The time period the peak starts at
        :param peak_end: The time period the peak ends at
        :return: Returns if meets day and time requirements
    """
    if in_peak_day(billing_time, peak_months, peak_days):
        if in_peak_time(billing_time, peak_start, peak_end):
            return True
    return False


def in_peak_day(billing_time: datetime,
                peak_months: List[int] = [12, 1, 2],
                peak_days: List[int]= [0, 1, 2, 3, 4, 5, 6]
                ) -> bool:
    """ Calculate if billing period falls on a peak day
        :param billing_time: The datetime to check (period ending)
        :param peak_months: List of months that peak applies
        :param peak_days: List of days of week that peak applies
                          (where 0 is Sunday and 6 is Saturday)
        :return: Returns if meets day requirements
    """

    day_of_week = int(billing_time.strftime('%w'))
    if billing_time.month in peak_months and day_of_week in peak_days:
        return True
    return False


def in_peak_time(billing_time: datetime,
                 peak_start: time = time(15, 0, 0),
                 peak_end: time = time(21, 30, 0)
                 ) -> bool:
    """ Calculate if billing period falls in peak time period
        :param billing_time: The datetime to check (period ending)
        :param peak_start: The time period the peak starts at
        :param peak_end: The time period the peak ends at
        :return: Returns if meets time requirements
    """
    if peak_start < billing_time.time() <= peak_end:
        return True
    return False
