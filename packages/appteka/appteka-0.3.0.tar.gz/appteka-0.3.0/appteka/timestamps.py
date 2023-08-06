# appteka - helpers collection

# Copyright (C) 2018 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Work with string timestamps. """

import time
import datetime


def get_time(secs, scale="s"):
    """
    Return time from timestamp.

    Parameters
    ----------
    secs : float
        Seconds since the epoch.
    scale : str
        Scale. Possible values: "ms" (milliseconds), "s" (seconds),
        "m" (minutes), "h" (hours).

    Returns
    -------
    label : str
        String label representing the time.

    """
    gmt = time.gmtime(secs)
    if scale == "s":
        return time.strftime("%H:%M:%S", gmt)
    elif scale == "m":
        return time.strftime("%H:%M", gmt)
    elif scale == "h":
        return time.strftime("%H", gmt)
    elif scale == "ms":
        millisecs = int(1000*(secs - int(secs)))
        return time.strftime("%H:%M:%S", secs) + ".{}".format(millisecs)


def get_date(secs):
    """
    Return date from timestamp.

    Parameters
    ----------
    secs : float
        Seconds since the epoch.

    Returns
    -------
    Returns
    -------
    label : str
        String label representing the date.

    """
    gmt = time.gmtime(secs)
    return time.strftime("%y-%m-%d", gmt)


class TimeFormat:
    """ Base class for string time formats. """
    @staticmethod
    def check(time_list):
        """ Check if timestamps in list corresponds to the format."""
        raise NotImplementedError

    @staticmethod
    def convert(str_time):
        """ Convert timestamp from string to seconds since the epoch. """
        raise NotImplementedError


class SecDotFormat(TimeFormat):
    """ Example: 1505314800.04 """
    @staticmethod
    def check(time_list):
        """ Check if timestamps in list corresponds to the format."""
        float_times = []
        for str_time in time_list:
            try:
                float_time = float(str_time)
                float_times.append(float_time)
            except ValueError:
                return False
        for t_current, t_next in zip(float_times[:-1], float_times[1:]):
            if t_current >= t_next:
                return False
        return True

    @staticmethod
    def convert(str_time):
        """ Convert timestamp from string to seconds since the epoch. """
        res = float(str_time)
        return res


class SecDotMsecFormat(TimeFormat):
    """ Examples: 1505314800.20, 1505314800.200 """
    @staticmethod
    def check(time_list):
        """ Check if timestamps in list corresponds to the format."""
        float_times = []
        for str_time in time_list:
            try:
                float_time = float(str_time)
                float_times.append(float_time)
            except ValueError:
                return False
        for t_current, t_next in zip(float_times[:-1], float_times[1:]):
            if t_current >= t_next:
                return True
        return False

    @staticmethod
    def convert(str_time):
        """ Convert timestamp from string to seconds since the epoch. """
        parts = str_time.split(".")
        left = parts[0]
        right = parts[1]
        if len(right) == 2:
            right = '0' + right
        res = float(left + '.' + right)
        return res


class SecCommaFormat(TimeFormat):
    """ Example: 1505314800,04 """
    @staticmethod
    def check(time_list):
        """ Check if timestamps in list corresponds to the format."""
        float_times = []
        for str_time in time_list:
            if ',' not in str_time:
                return False
            str_time_dot = str_time.replace(',', '.')
            try:
                float_time = float(str_time_dot)
                float_times.append(float_time)
            except ValueError:
                return False
        return True

    @staticmethod
    def convert(str_time):
        """ Convert timestamp from string to seconds since the epoch. """
        str_time_dot = str_time.replace(',', '.')
        res = float(str_time_dot)
        return res


class DateTimeFormat(TimeFormat):
    """ Examples: '31/10/2017 16:30:00.000' or '12.07.2017
        21:00:00.160000' """
    @staticmethod
    def check(time_list):
        """ Check if timestamps in list corresponds to the format."""
        for str_time in time_list:
            if ' ' not in str_time:
                return False
        return True

    @staticmethod
    def convert(str_time):
        """ Convert timestamp from string to seconds since the epoch. """
        splitted = str_time.replace("/", " ").\
            replace(":", " ").\
            replace(".", " ").\
            split()
        secs = datetime.datetime(
            int(splitted[2]),  # year
            int(splitted[1]),  # month
            int(splitted[0]),  # day
            int(splitted[3]),  # hours
            int(splitted[4]),  # minutes
            int(splitted[5])   # seconds
        ).timestamp()
        res = secs + float("0."+splitted[6])  # milliseconds
        return res


class TimeConverter:
    """ Converter from string timestamp to seconds since the epoch. """
    def __init__(self):
        self.formats = [
            SecDotFormat,
            SecCommaFormat,
            SecDotMsecFormat,
            DateTimeFormat,
        ]
        self.fmt = None

    def learn(self, str_times):
        """ Attempt to recognize time format. """
        for fmt in self.formats:
            if fmt.check(str_times):
                self.set_format(fmt)
                return True
        return False

    def set_format(self, fmt):
        """ Set format. Can be used for manual set up converter. """
        self.fmt = fmt

    def convert(self, str_time):
        """ Convert timestamp from string to seconds since the epoch. """
        if self.fmt is None:
            raise RuntimeError("Unknown time format.")
        res = self.fmt.convert(str_time)
        return res


def example():
    """ Example of using Converter. """
    list_of_ts = [
        '1505314800.0',
        '1505314800.2',
        '1505314800.4',
        '1505314800.6',
        '1505314800.8',
        '1505314800.10',
        '1505314800.12',
        '1505314800.14',
        '1505314800.16',
    ]
    # list_of_ts = [
    #     '31/10/2017 16:30:00.000',
    #     '31/10/2017 16:30:01.000',
    # ]
    converter = TimeConverter()
    if not converter.learn(list_of_ts):
        print("Unknown format")
        exit()
    for str_time in list_of_ts:
        sste = converter.convert(str_time)
        print(sste)


if __name__ == "__main__":
    example()
