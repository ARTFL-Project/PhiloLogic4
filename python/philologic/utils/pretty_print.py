#!/usr/bin/env python3


def pretty_print(value, htchar='\t', lfchar='\n', indent=0):
    '''Pretty printing from a Stack Overflow answer:
    http://stackoverflow.com/questions/3229419/pretty-printing-nested-dictionaries-in-python#answer-26209900.'''
    nlch = lfchar + htchar * (indent + 1)
    if type(value) is dict:
        if value:
            items = [nlch + repr(key) + ': ' + pretty_print(value[key], htchar, lfchar, indent + 1) for key in value]
            return '{%s}' % (','.join(items) + lfchar + htchar * indent)
        else:
            return "{}"
    elif type(value) is list:
        if value:
            items = [nlch + pretty_print(item, htchar, lfchar, indent + 1) for item in value]
            return '[%s]' % (','.join(items) + lfchar + htchar * indent)
        else:
            return "[]"
    elif type(value) is tuple:
        if value:
            items = [nlch + pretty_print(item, htchar, lfchar, indent + 1) for item in value]
            return '(%s)' % (','.join(items) + lfchar + htchar * indent)
        else:
            return "()"
    else:
        return repr(value)
