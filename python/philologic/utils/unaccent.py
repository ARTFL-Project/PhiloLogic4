#!/usr/bin/env python

import unicodedata

def smash_accents(char):
    try:
        return ''.join([i for i in unicodedata.normalize("NFKD", char) if not unicodedata.combining(i)])
    except TypeError:
        return ''.join([i for i in unicodedata.normalize("NFKD", char.decode('utf8')) if not unicodedata.combining(i)])
