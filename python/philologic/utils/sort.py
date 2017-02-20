#!/usr/bin/env python3

from natsort import natsorted

from .unaccent import smash_accents

def sort_list(list_to_sort, sort_keys):
    def make_sort_key(d):
        key = [smash_accents(d.get(f, "ZZZZZ")) for f in sort_keys]
        return key

    return natsorted(list_to_sort, key=make_sort_key, reverse=False)
