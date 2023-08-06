"""
    energy_shaper.splitter
    ~~~~~
    Break usage details down into smaller periods
"""

import logging
from math import ceil
from statistics import mean
from typing import Tuple, Iterable, List
from datetime import datetime, timedelta
import calendar
from . import Reading


def split_into_profiled_intervals(records: Iterable[Reading],
                                  interval_m: int = 30,
                                  profile: List[float] = [0.05, 0.07, 0.12, 0.11,
                                                          0.14, 0.14, 0.27, 0.10
                                                          ]
                                  ):
    """ Split load data into daily billing intervals if larger

    :param records: Tuple in the form of (start_date, end_date, usage)
                    Records must be a day or less in duration
    :param interval_m: The interval length in minutes
    :param profile: The profile to use to scale results
    :return: Yield the split up intervals
    """

    day_intervals = int(24 * 60 / interval_m)
    scaled_profile = transform_load_shape(profile, num_intervals=day_intervals)

    for record in records:
        start_date = record[0]
        end_date = record[1]
        usage = record[2]
        rec_interval = int((end_date - start_date).total_seconds() / 60)
        if rec_interval <= interval_m:
            # Already less then interval so return as is
            yield Reading(start_date, end_date, usage)
        elif rec_interval > 24 * 60:
            raise ValueError(
                'Records must be split into daily (or smaller) intervals first')
        elif rec_interval == 24 * 60:
            # A day's record, apply the provided load profile
            intervals = list(split_into_intervals(
                start_date, end_date, interval_m))
            for i, (period_start, period_end) in enumerate(intervals):
                split_usage = scaled_profile[i] * usage
                yield Reading(period_start, period_end, split_usage)

        else:
            # Smaller than a day, just split evenly
            intervals = list(split_into_intervals(
                start_date, end_date, interval_m))
            # Split evenly by number of intervals returned
            # The last interval could potentially have a smaller duration
            split_usage = usage / len(intervals)
            for period_start, period_end in intervals:
                yield Reading(period_start, period_end, split_usage)



def transform_load_shape(profile: List[float],
                         num_intervals: int = 48) -> List[float]:
    """ Split load data into daily billing intervals if larger

    :param profile: The profile to use to scale results
    :param num_invervals: The number of intervals to split into
    :return: A modifed load profile
    """
    num_intervals = int(num_intervals)
    # Stretch list to match num_intervals
    if len(profile) == num_intervals:
        new_profile = profile
    elif len(profile) % num_intervals == 0 or num_intervals % len(profile) == 0:
        new_profile = [None] * num_intervals
        repeat = num_intervals / len(profile)
        for i, _ in enumerate(new_profile):
            j = ceil((i + 1) / repeat) - 1
            new_profile[i] = profile[j]
    else:
        logging.error(
            'The number of intervals [%s] can not match the profile length [%s] provided', num_intervals, len(profile))
        new_profile = [1] * num_intervals

    # Scale the list to total 100%
    scale = 1 / sum(new_profile)
    new_profile = [i * scale for i in new_profile]
    return new_profile


def split_into_daily_intervals(records: Iterable[Reading]):
    """ Split load data into daily billing intervals if larger

    :param records: Tuple in the form of (start_date, end_date, usage)
    :return: Yield the split up intervals
    """
    for record in records:
        start_date = record[0]
        end_date = record[1]
        usage = record[2]
        interval_s = int((end_date - start_date).total_seconds())
        interval_days = interval_s / 60 / 60 / 24

        if interval_days <= 1.0:
            # Don't need to do anything
            yield Reading(start_date, end_date, usage)
        else:
            intervals = list(split_into_intervals(
                start_date, end_date, interval_m=60 * 24))
            # Split evenly by number of intervals returned
            # The last interval could potentially have a smaller duration
            daily_usage = usage / len(intervals)
            for period_start, period_end in intervals:
                yield Reading(period_start, period_end, daily_usage)


def split_into_intervals(start_date: datetime, end_date: datetime,
                         interval_m: float = 30
                         ) -> Iterable[Tuple[datetime, datetime]]:
    """ Generate equally spaced intervals between two dates

    :param start_date: The starting date range
    :param end_date: The ending date range
    :param interval_m: The interval between ranges in minutes
    :return: Start and end type for each interval generated
    """
    delta = timedelta(seconds=interval_m * 60)
    period_start = start_date
    period_end = start_date + delta
    if period_end >= end_date:
        logging.warning('Interval is too large to split further')
        yield (period_start, period_end)
    else:
        while period_start < end_date:
            if period_end > end_date:
                yield (period_start, end_date)
            else:
                yield (period_start, period_end)
            period_start += delta
            period_end += delta
