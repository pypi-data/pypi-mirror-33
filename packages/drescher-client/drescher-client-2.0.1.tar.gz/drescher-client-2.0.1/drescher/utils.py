# coding: utf-8

from datetime import datetime
from uuid import UUID


def to_date(date_string, format='%Y-%m-%d %H:%M:%S'):
    date_string = date_string.split('+')[0]

    return datetime.strptime(date_string, format)


def to_uuid(hex):
    return UUID(hex)
