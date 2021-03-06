# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

import datetime

import six
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext

__all__ = ("parse_date", "parse_time", "try_parse_date", "try_parse_time")

_date_formats = (
    "%Y-%m-%d",
    "%Y%m%d",
    "%Y/%m/%d",
    "%d.%m.%y",
    "%d.%m.%Y",
    "%Y %m %d",
    "%m/%d/%Y",
)

_time_formats = (
    "%H:%M:%S",
    "%H:%M",
)

locale_year_and_month_formats = {
    # Sourced from the Unicode CLDR, version 27.1.
    # All locales not listed here use "MMM y".
    'be': 'LLL y',
    'bg': "MM.y 'г'.",
    'bs': 'MMM y.',
    'ca': 'LLL y',
    'cs': 'LLLL y',
    'dz': 'y སྤྱི་ཟླ་MMM',
    'eu': 'y MMM',
    'fi': 'LLL y',
    'fo': 'y MMM',
    'hr': 'LLL y.',
    'hu': 'y. MMM',
    'hy': 'yթ. LLL',
    'ja': 'y年M月',
    'ka': 'MMM, y',
    'kea': "MMM 'di' y",
    'ko': 'y년 MMM',
    'ky': "y-'ж'. MMM",
    'lt': 'y-MM',
    'lv': "y. 'g'. MMM",
    'mk': "MMM y 'г'.",
    'ml': 'y MMM',
    'mn': 'y MMM',
    'ne': 'y MMM',
    'os': 'LLL y',
    'pl': 'MM.y',
    'pt': 'MM/y',
    'ru': 'LLL y',
    'seh': "MMM 'de' y",
    'si': 'y MMM',
    'sk': 'LLLL y',
    'sr': 'MMM y.',
    'uk': 'LLL y',
    'uz': 'y MMM',
}


def _parse_date_str(value):
    value = value.strip()
    for fmt in _date_formats:
        try:
            return datetime.datetime.strptime(value, fmt).date()
        except:
            pass
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f").date()
    except:
        pass


def _parse_time_str(value):
    value = value.strip()
    for fmt in _time_formats:
        try:
            return datetime.datetime.strptime(value, fmt).time()
        except:
            pass
    return None


def parse_date(value):
    """
    Tries to make a date out of the value. If impossible, it raises an exception.

    :param value: A value of some ilk.
    :return: Date
    :rtype: datetime.date
    :raise ValueError:
    """
    # this should be first since `datetime.datetime` is subclass of `datetime.date`
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    elif isinstance(value, six.string_types):
        date = _parse_date_str(value)
        if not date:
            raise ValueError("Unable to parse %s as date." % value)
        return date
    raise ValueError("Unable to parse %s as date (unknown type)." % value)


def parse_time(value):
    """
    Tries to make a time out of the value. If impossible, it raises an exception.

    :param value: A value of some ilk.
    :return: Time
    :rtype: datetime.time
    :raise ValueError:
    """
    if isinstance(value, datetime.time):
        return value
    if isinstance(value, datetime.datetime):
        return value.time()
    if isinstance(value, six.string_types):
        time = _parse_time_str(value)
        if not time:
            raise ValueError("Unable to parse %s as date." % value)
        return time
    raise ValueError("Unable to parse %s as date (unknown type)." % value)


def try_parse_date(value):
    """
    Tries to make a time out of the value. If impossible, returns None.

    :param value: A value of some ilk.
    :return: Date
    :rtype: datetime.date
    """
    if value is None:
        return None
    try:
        return parse_date(value)
    except ValueError:
        return None


def try_parse_time(value):
    """
    Tries to make a time out of the value. If impossible, returns None.

    :param value: A value of some ilk.
    :return: Time
    :rtype: datetime.time
    """
    if value is None:
        return None
    try:
        return parse_time(value)
    except ValueError:
        return None


def get_year_and_month_format(locale):
    """
    Get the Babel/Unicode format string for a "year and month" format
    for the given locale.

    Only the "language" part of the locale is taken into account here.

    :param locale: Babel locale
    :type locale: babel.Locale
    :return: format string
    :rtype: str
    """
    return locale_year_and_month_formats.get(locale.language.lower(), "MMM y")


def to_aware(date, time=datetime.time.min, tz=None):
    """
    Convert date or datetime to aware datetime.

    :type date: datetime.date|datetime.datetime
    :param date:
      Date or datetime object to convert
    :type time: datetime.time
    :param time:
      Time value for supplementing dates to datetimes, default 0:00:00
    :type tz: datetime.tzinfo|None
      Timezone to use, default ``timezone.get_current_timezone()``
    :rtype: datetime.datetime
    :return:
      Converted aware datetime object
    """
    if isinstance(date, datetime.datetime):
        if timezone.is_aware(date):
            return date
        return timezone.make_aware(date, timezone=tz)
    assert isinstance(date, datetime.date), '%r should be date' % (date,)
    combined = datetime.datetime.combine(date, time)
    return timezone.make_aware(combined, timezone=tz)


def local_now(tz=None):
    """
    Get current time as aware datetime in local timezone.

    :type tz: datetime.tzinfo|None
      Timezone to use, default ``timezone.get_current_timezone()``
    :rtype: datetime.datetime
    """
    return timezone.localtime(to_aware(timezone.now()), timezone=tz)


def to_datetime_range(start, end):
    for value in [start, end]:
        if not isinstance(value, datetime.date):
            raise TypeError("Not date or datetime: {!r}".format(value))
    start_is_datetime = isinstance(start, datetime.datetime)
    end_is_datetime = isinstance(end, datetime.datetime)
    if start_is_datetime != end_is_datetime:
        raise TypeError("Start and end must be same type: {!r} - {!r}"
                        .format(start, end))
    # Add +1 day to end if it's a date to make the range inclusive
    end_delta = datetime.timedelta(days=(1 if not end_is_datetime else 0))
    return (to_aware(start), to_aware(end) + end_delta)


class DurationRange(object):
    """
    Present duration range, min days to max days.
    """
    def __init__(self, min_duration, max_duration=None):
        assert isinstance(min_duration, datetime.timedelta)
        assert max_duration is None or (
            isinstance(max_duration, datetime.timedelta))
        assert max_duration is None or max_duration >= min_duration
        self.min_duration = min_duration
        self.max_duration = (max_duration if max_duration is not None
                             else min_duration)

    @classmethod
    def from_days(cls, min_days, max_days=None):
        return cls(
            datetime.timedelta(days=min_days),
            (datetime.timedelta(days=max_days)
             if max_days is not None else None))

    def __str__(self):
        if self.min_duration == self.max_duration:
            days = self.max_duration.days
            return ungettext("%s day", "%s days", days) % (days,)
        return _("%(min)s--%(max)s days") % {
            "min": self.min_duration.days, "max": self.max_duration.days}
