"""
    energy_shaper.models
    ~~~~~
    Data class definitions
"""

from datetime import datetime
from typing import NamedTuple

class Reading(NamedTuple):
    """ Represents an daily summary """
    start: datetime
    end: datetime
    usage: float

    def __repr__(self) -> str:
        values = f'start={self.start}, end={self.end}, usage {self.usage:.2f}'
        return f'<Reading {values}>'

class DaySummary(NamedTuple):
    """ Represents an daily summary """
    day: datetime
    total: float
    peak: float
    shoulder: float
    offpeak: float

    def __repr__(self) -> str:
        return f'<DaySummary {self.day:%Y-%m-%d} Usage:{self.total:.2f}>'
