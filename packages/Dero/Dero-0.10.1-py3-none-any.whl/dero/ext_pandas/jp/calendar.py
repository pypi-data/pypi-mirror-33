from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday, \
     sunday_to_monday, DateOffset, MO
from dero.ext_pandas.jp.equinox import vernal_equinox, autumnal_equinox

class JapanTradingCalendar(AbstractHolidayCalendar):
    rules=[
        Holiday('USNewYearsDay', month=1, day=1),
        Holiday(name="JPNewYearsDay2", month=1, day=2),
        Holiday(name="JPNewYearsDay3", month=1, day=3),
        Holiday(name="Coming of Age Day", month=1, day=1, offset=DateOffset(weekday=MO(2))),
        Holiday(name="National Founding day", month=2, day=11, observance=sunday_to_monday),
        Holiday(name="Vernal Equinox", month=3, day=20, observance=vernal_equinox),
        Holiday(name="Showa day", month=4, day=29, observance=sunday_to_monday),
        Holiday(
            name="Constitution memorial day",
            month=5,
            day=3,
            observance=sunday_to_monday,
        ),
        Holiday(
            name="Greenery day",
            month=5,
            day=4,
            observance=sunday_to_monday,
        ),
        Holiday(
            name="Children's day",
            month=5,
            day=5,
            observance=sunday_to_monday,
        ),
        Holiday(
            name="Marine day",
            month=7,
            day=1,
            offset=DateOffset(weekday=MO(3)),
        ),
        Holiday(
            name="Mountain day",
            month=8,
            day=11,
            observance=sunday_to_monday,
        ),
        Holiday(
            name="Respect for the aged day",
            month=9,
            day=1,
            offset=DateOffset(weekday=MO(3)),
        ),
        Holiday(
            name="Autumnal equinox",
            month=9,
            day=22,
            observance=autumnal_equinox,
        ),
        Holiday(
            name="Health and sports day",
            month=10,
            day=1,
            offset=DateOffset(weekday=MO(2)),
        ),
        Holiday(
            name="Culture day",
            month=11,
            day=3,
            observance=sunday_to_monday,
        ),
        Holiday(
            name="Labor Thanksgiving Day",
            month=11,
            day=23,
            observance=sunday_to_monday,
        ),
        Holiday(
            name="Emperor's Birthday",
            month=12,
            day=23,
            observance=sunday_to_monday,
        ),
        Holiday(
            name="Before New Year's Day",
            month=12,
            day=31,
            observance=sunday_to_monday,
        ),
    ]