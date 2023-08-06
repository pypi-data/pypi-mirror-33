"""
Some useful functions.
"""


import json
import re
from datetime import datetime
from collections import namedtuple, UserList
from functools import reduce
from os.path import join, dirname
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
import pycountry

def parse_date(date_string):
    """Parse a date string with the format '%Y-%m-%dT%H:%M:%S.%fZ'.

    Args:
        date_string (str): string with the format '%Y-%m-%dT%H:%M:%S.%fZ'
    Returns:
        datetime
    """
    return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')


def check_date(date_object):
    """Convert a date into the right for API"""
    if date_object is None: return None
    if isinstance(date_object, str):
        date_object = parse(date_object)
    date_object = date_object.isoformat()
    return date_object


def check_language(language):
    """Check if a language code or object is correct"""
    if isinstance(language, (list, tuple)):
        return [check_language(item) for item in language]
    elif language in pycountry.languages:
        return language.alpha_2
    else:
        try:
            pycountry.languages.get(alpha_2=language)
        except KeyError:
            raise ValueError("{} is an unknown language code.".format(
                language
            ))
        return language


def check_geocode(country):
    """Check if a country code or object is correct"""
    if isinstance(country, (list, tuple)):
        return [check_geocode(item) for item in country]
    elif country in pycountry.countries:
        return country.alpha_2
    else:
        try:
            pycountry.countries.get(alpha_2=country)
        except KeyError:
            raise ValueError("{} is an unknown geocode.".format(
                country
            ))
        return country


def check_list(elements, rtype, assertion_message=None):
    """Check if all the items of a list has the right type"""
    error_message = "Please enter an argument of type {}".format(rtype)
    assertion_message = assertion_message or error_message
    assert all([isinstance(element, rtype) for element in elements]), \
        assertion_message


def load_data(filepath):
    """Load static file located in the package directory"""
    filepath = join(dirname(__file__), filepath)
    with open(filepath, mode='r') as data_file:
        data = json.load(data_file)
    return data


def dict_to_namedtuple(name, data):
    """Converts a dictionary into a namedtuple"""
    return namedtuple(name, data.keys())(**data)


def to_snake_case(name):
    """Converts a string into camel_case format"""
    name = name.replace('-', '_')
    temp = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', temp).lower()


flat = lambda x: reduce(lambda a, b: a+b, x, [])


class SelfDict(dict):
    """Dict which return the key if it was not found. It also try to convert
    the key into an integer"""
    def __missing__(self, key):
        try:
            key = int(key)
        except KeyError:
            pass
        if key in self:
            return self[key]
        return str(key)

    def __call__(self, key):
        return self[key]


def dumps_datetime(date):
    """Datetime into string"""
    if isinstance(date, datetime):
        return date.__str__()
    return None


def parse_image_filename(filename):
    """Parse the image filename using a regular expression.

    Returns:
        re.SRE_Match:
    """
    pattern = re.compile(r'/(?P<filename>[0-9a-zA-Z_]*).(?P<format>[a-z]*)$')
    match = pattern.search(filename)
    if match:
        return match.group('filename'), match.group('format')
    return None, None


class Quarter(UserList):
    """List object storing start date and end date of a quarter"""
    def __init__(self, n_quarter, year):
        super().__init__()
        self.n_quarter = n_quarter
        self.year = year
        start = datetime(year, 1, 1)
        start_quarter = list(
            rrule(MONTHLY, interval=3, dtstart=start, count=4)
        )[n_quarter - 1]
        end_quarter = start_quarter + relativedelta(months=3, days=-1)
        self.data.extend([start_quarter, end_quarter])

    def __contains__(self, value):
        return value >= self[0] and value <= self[1]

    @classmethod
    def of_year(cls, year):
        """Generates all Quarter object of a specific year"""
        start = datetime(year, 1, 1)
        start_quarter = list(
            rrule(MONTHLY, interval=3, dtstart=start, count=4)
        )
        end_quarter = [
            date + relativedelta(months=3, days=-1) for date in start_quarter
        ]
        return [cls(*item) for item in list(zip(start_quarter, end_quarter))]

    def __repr__(self):
        return 'Quarter(nth={}, year={})'.format(
            1 + self.data[0].month // 3,
            self.data[0].year
        )
