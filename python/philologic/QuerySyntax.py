#!/usr/bin/env python
import re

patterns = [("QUOTE",r'".+?"'),
            ("QUOTE", r'".+'),
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

def group_terms(parsed):
    grouped = []
    current_clause = []
    last_term = None
    for kind,val in parsed:
        if last_term == "RANGE":
            # immediately detach ranges for now.
            grouped.append(current_clause)
            current_clause = []

        if kind == "TERM" or kind == "QUOTE" or kind == "NULL":
            if  last_term != "OR" and last_term != "NOT":
                grouped.append(current_clause)
                current_clause = []
        elif kind == "OR":
            pass
        elif kind == "RANGE":
            # RANGE should immediately detach a new clause and then close it.
            if last_term != "NOT":
                grouped.append(current_clause)
                current_clause = []
        elif kind == "NOT":
            # NOT should be put in the same clause as it's predecessors
            pass
        current_clause.append((kind,val))
        last_term = kind
    grouped.append(current_clause)
    # filter out possible empty groups
    grouped = [g for g in grouped if g != []]
    return grouped
