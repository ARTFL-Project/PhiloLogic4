#!/usr/bin/env python


def pretty_print(value, htchar='\t', lfchar='\n', indent=0):
    '''Pretty printing heavily inspired from a Stack Overflow answer:
    http://stackoverflow.com/questions/3229419/pretty-printing-nested-dictionaries-in-python#answer-26209900.'''
    nlch = lfchar + htchar * (indent + 1)
    if type(value) is dict:
        if value:
            if len(value) == 1:
                return "{%s: %s}" % (repr(value.keys()[0]), pretty_print(value.values()[0]))
            else:
                items = [nlch + repr(key) + ': ' + pretty_print(value[key], htchar, lfchar, indent + 1) for key in value]
                return '{%s}' % (','.join(items) + lfchar + htchar * indent)
        else:
            return "{}"
    elif type(value) is list:
        if value:
            if len(value) == 1:
                return "[%s]" % pretty_print(value[0])
            else:
                items = [nlch + pretty_print(item, htchar, lfchar, indent + 1) for item in value]
                return '[%s]' % (','.join(items) + lfchar + htchar * indent)
        else:
            return "[]"
    elif type(value) is tuple:
        if value:
            if len(value) == 1:
                return "(%s)" % pretty_print(value[0])
            else:
                items = [nlch + pretty_print(item, htchar, lfchar, indent + 1) for item in value]
                return '(%s)' % (','.join(items) + lfchar + htchar * indent)
        else:
            return "()"
    else:
        return repr(value)
