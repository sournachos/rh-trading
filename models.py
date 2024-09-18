from enum import Enum


class OptionType(str, Enum):
    call = "call"
    put = "put"


class Interval(str, Enum):
    five_min = "5minute"
    ten_min = "10minute"
    hour = "hour"
    day = "day"
    week = "week"


class Span(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    three_months = "3months"
    year = "year"
    five_years = "5year"


class Bounds(str, Enum):
    regular = "regular"
    trading = "trading"
    extended = "extended"
