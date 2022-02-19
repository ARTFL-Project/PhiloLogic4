#!/usr/bin/env python3

from natsort import natsorted

from unidecode import unidecode


def sort_list(list_to_sort, sort_keys):
    """Sort strings converted to ascii"""

    def make_sort_key(d):
        key = [unidecode(d.get(f, "ZZZZZ")) for f in sort_keys]
        return key

    return natsorted(list_to_sort, key=make_sort_key, reverse=False)
