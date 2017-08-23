#!/usr/bin/env python

from __future__ import absolute_import
import six.moves.html_entities
import re


entities_match = re.compile("&#?\w+;")

def convert_entities(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(six.moves.html_entities.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    try:
        return entities_match.sub(fixup, text)
    except UnicodeDecodeError:
        return entities_match.sub(fixup, text.decode('utf8', 'ignore'))
