#!/usr/bin/env python3


import unicodedata

def smash_accents(char):
    """Smash accents"""
    try:
        return int(char)
    except ValueError:
        return ''.join([i for i in unicodedata.normalize("NFKD", char) if not unicodedata.combining(i)])
