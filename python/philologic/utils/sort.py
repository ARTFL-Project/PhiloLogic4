#!/usr/bin/env python3

import datetime

from natsort import natsorted
from unidecode import unidecode


def get_key(d, f):
    key = d.get(f, "ZZZZZ")
    if isinstance(key, datetime.date):
        return f"{key.year}-{key.month}-{key.day}"
    elif isinstance(key, int):
        return key
    else:
        return unidecode(key)


def sort_list(list_to_sort, sort_keys):
    """Sort strings converted to ascii"""

    def make_sort_key(d):
        key = [get_key(d, f) for f in sort_keys]
        return key

    return natsorted(list_to_sort, key=make_sort_key, reverse=False)
