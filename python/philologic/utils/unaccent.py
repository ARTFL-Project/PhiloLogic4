#!/usr/bin/env python3


import unicodedata


def smash_accents(char):
    """Smash accents"""
    return "".join([i for i in unicodedata.normalize("NFKD", char) if not unicodedata.combining(i)])
