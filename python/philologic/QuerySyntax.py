#!/usr/bin/env python
import re

patterns = [("QUOTE",r'".+?"'),
            ("NOT","NOT"),
            ('OR',r'\|'),
            ('RANGE',r'[^|\s]+?\-[^|\s]+'),
            ('NULL',r'NULL'),
            ('TERM',r'[^\-|\s"]+')]
            
def parse_query(qstring):
    buf = qstring[:]
    parsed = []
    while len(buf) > 0:
        for label,pattern in patterns:
            m = re.match(pattern,buf)
            if m:
                parsed.append((label,m.group()))
                buf = buf[m.end():]
                break
        else:
            buf = buf[1:]
    return parsed
