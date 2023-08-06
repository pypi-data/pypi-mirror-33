"""
    energy_shaper.grouper
    ~~~~~
    Group energy readings into daily and monthly values
"""
import logging
from datetime import datetime, time, timedelta
from typing import Tuple, Iterable, List
from math import isclose
from . import split_into_daily_intervals
from . import split_into_profiled_intervals
from . import in_peak_period
from . import Reading, DaySummary


def group_into_daily_summary(records: List[Reading],
                             profile: List[float] = [0.05,  0.07,  0.12,  0.11,
                                                     0.14,  0.14,  0.27, 0.10
                                                     ],
                             peak_months: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                             peak_days: List[int] = [0, 1, 2, 3, 4],
                             peak_start: time = time(16, 0, 0),
                             peak_end: time = time(20, 0, 0),
                             shoulder_months: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                             shoulder_days: List[int] = [0, 1, 2, 3, 4, 5, 6],
                             shoulder_start: time = time(7, 0, 0),
                             shoulder_end: time = time(22, 0, 0),
                             ):
    """ Group load data into billing intervals, if larger split first

    :param records: Tuple in the form of (start_date, end_date, usage)
                    Records must be a day or less in duration
    :param interval_m: The interval length in minutes
    :param profile: The profile to use to scale results
    :return: Yield the daily summaries
    """
    records = group_into_profiled_intervals(records, interval_m=5,
                                            profile=profile)

    group_total = dict()
    group_peak = dict()
    group_shoulder = dict()
    group_offpeak = dict()

    for record in records:
        start_date = record[0]
        end_date = record[1]
        usage = record[2]

        # Increment Daily Totals
        group_day = start_date.strftime('%Y-%m-%d')
        if group_day not in group_total:
            group_total[group_day] = usage
        else:
            group_total[group_day] += usage

        if in_peak_period(billing_time=end_date,
                          peak_months=peak_months, peak_days=peak_days,
                          peak_start=peak_start, peak_end=peak_end
                          ):
            if group_day not in group_peak:
                group_peak[group_day] = usage
            else:
                group_peak[group_day] += usage
        elif in_peak_period(billing_time=end_date,
                            peak_months=shoulder_months, peak_days=shoulder_days,
                            peak_start=shoulder_start, peak_end=shoulder_end
                            ):
            if group_day not in group_shoulder:
                group_shoulder[group_day] = usage
            else:
                group_shoulder[group_day] += usage
        else:
            if group_day not in group_offpeak:
                group_offpeak[group_day] = usage
            else:
                group_offpeak[group_day] += usage

    # Output grouped values as list
    for group_day in sorted(group_total.keys()):

        total = group_total[group_day]
        try:
            peak = group_peak[group_day]
        except KeyError:
            peak = 0.0
        try:
            shoulder = group_shoulder[group_day]
        except KeyError:
            shoulder = 0.0
        try:
            offpeak = group_offpeak[group_day]
        except KeyError:
            offpeak = 0.0

        assert isclose(total, peak + shoulder + offpeak)
        day = datetime.strptime(group_day, '%Y-%m-%d')
        yield DaySummary(day, total, peak, shoulder, offpeak)


def group_into_profiled_intervals(records: Iterable[Reading],
                                  interval_m: int = 30,
                                  profile: List[float] = [0.05,  0.07,  0.12,  0.11,
                                                          0.14,  0.14,  0.27, 0.10
                                                          ]
                                  ):
    """ Group load data into billing intervals, if larger split first

    :param records: Tuple in the form of (start_date, end_date, usage)
                    Records must be a day or less in duration
    :param interval_m: The interval length in minutes
    :param profile: The profile to use to scale results
    :return: Yield the split up intervals
    """

    if interval_m > 60.0:
        raise ValueError('Interval must be 60m or less ')

    records = split_into_daily_intervals(records)
    records = split_into_profiled_intervals(records, interval_m, profile)

    group_records = dict()
    for record in records:
        start_date = record[0]
        end_date = record[1]
        usage = record[2]

        # Check interval
        rec_interval = int((end_date - start_date).total_seconds()/60)
        assert rec_interval <= interval_m

        # Increment dictionary value
        group_end = get_group_end(end_date)
        if group_end not in group_records:
            group_records[group_end] = usage
        else:
            group_records[group_end] += usage

    # Output grouped values as list
    for key in sorted(group_records.keys()):
        end = key
        start = end - timedelta(minutes=interval_m)
        yield Reading(start, end, group_records[key])


def get_group_end(end_date: datetime, interval_m: int = 30
                  ) -> datetime:
    """ Get interval group end time

    :return: Return the end of the interval period
    """
    group_end = end_date
    while group_end.minute % interval_m != 0:
        group_end += timedelta(minutes=1)
    return group_end
