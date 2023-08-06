#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2018 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""tools to help manipulating time and dates"""

from sat.core.constants import Const as C
import datetime
from dateutil import parser as dateutil_parser
from babel import dates
import calendar
import time


def date_parse(value):
    """Parse a date and return corresponding unix timestamp

    @param value(unicode): date to parse, in any format supported by dateutil.parser
    @return (int): timestamp
    """
    return calendar.timegm(dateutil_parser.parse(unicode(value)).utctimetuple())


def date_fmt(
    timestamp,
    fmt="short",
    date_only=False,
    auto_limit=7,
    auto_old_fmt="short",
    auto_new_fmt="relative",
    locale_str=C.DEFAULT_LOCALE,
):
    """format date according to locale

    @param timestamp(basestring, int): unix time
    @param fmt(str): one of:
        - short: e.g. u'31/12/17'
        - medium: e.g. u'Apr 1, 2007'
        - long: e.g. u'April 1, 2007'
        - full: e.g. u'Sunday, April 1, 2007'
        - relative: format in relative time
            e.g.: 3 hours
            note that this format is not precise
        - iso: ISO 8601 format
            e.g.: u'2007-04-01T19:53:23Z'
        - auto: use auto_old_fmt if date is older than auto_limit
            else use auto_new_fmt
        - auto_day: shorcut to set auto format with change on day
            old format will be short, and new format will be time only
        or a free value which is passed to babel.dates.format_datetime
    @param date_only(bool): if True, only display date (not datetime)
    @param auto_limit (int): limit in days before using auto_old_fmt
        use 0 to have a limit at last midnight (day change)
    @param auto_old_fmt(unicode): format to use when date is older than limit
    @param auto_new_fmt(unicode): format to use when date is equal to or more recent
        than limit

    """
    if fmt == "auto_day":
        fmt, auto_limit, auto_old_fmt, auto_new_fmt = "auto", 0, "short", "HH:mm"
    if fmt == "auto":
        if auto_limit == 0:
            today = time.mktime(datetime.date.today().timetuple())
            if int(timestamp) < today:
                fmt = auto_old_fmt
            else:
                fmt = auto_new_fmt
        else:
            days_delta = (time.time() - int(timestamp)) / 3600
            if days_delta > (auto_limit or 7):
                fmt = auto_old_fmt
            else:
                fmt = auto_new_fmt

    if fmt == "relative":
        delta = int(timestamp) - time.time()
        return dates.format_timedelta(
            delta, granularity="minute", add_direction=True, locale=locale_str
        )
    elif fmt in ("short", "long"):
        formatter = dates.format_date if date_only else dates.format_datetime
        return formatter(int(timestamp), format=fmt, locale=locale_str)
    elif fmt == "iso":
        if date_only:
            fmt = "yyyy-MM-dd"
        else:
            fmt = "yyyy-MM-ddTHH:mm:ss'Z'"
        return dates.format_datetime(int(timestamp), format=fmt)
    else:
        return dates.format_datetime(int(timestamp), format=fmt, locale=locale_str)
