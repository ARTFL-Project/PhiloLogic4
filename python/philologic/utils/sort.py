#!/usr/bin/env python

import unicodedata

def __smash_accents(char):
    try:
        return [i for i in unicodedata.normalize("NFKD", char) if not unicodedata.combining(i)]
    except TypeError:
        return [i for i in unicodedata.normalize("NFKD", char.decode('utf8')) if not unicodedata.combining(i)]

def sort_list(list_to_sort, sort_keys):
    def make_sort_key(d):
        key = [__smash_accents(d[f]) for f in sort_keys]
        return key

    return list_to_sort.sort(key=make_sort_key, reverse=False)
