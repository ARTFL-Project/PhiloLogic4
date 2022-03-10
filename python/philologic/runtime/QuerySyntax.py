#!/usr/bin/env python3

import regex as re

patterns = [
    ("QUOTE", r'".+?"'),
    ("QUOTE", r'".+'),
    ("NOT", "NOT"),
    ("OR", r"\|"),
    ("RANGE", r"[^|\s]+?\-[^|\s]+"),
    ("RANGE", r"\d+\-\Z"),
    ("RANGE", r"\-\d+\Z"),
    ("NULL", r"NULL"),
    ("TERM", r'[^\-|\s"]+'),
]

# TODO: support quotes around a date, support range such as 1789-08-.* ???
date_patterns = [
    ("NOT", "NOT"),
    ("OR", r"\|"),
    ("DATE", r"(\d+-\d+-\d+)\Z"),
    ("YEAR", r"(\d+)\Z"),
    ("YEAR_MONTH", r"(\d+-\d+)\Z"),
    ("YEAR_MONTH_DAY", r"(\d+-\d+-\d+)\Z"),
    ("DATE_RANGE", r"([^<]+)<=>(.*)"),
]

YEAR_MONTH_DAY = re.compile(r"(\d+)-(\d+)-(\d+)")
YEAR_MONTH = re.compile(r"^(\d+)-(\d+)\Z")
YEAR = re.compile(r"^(\d+)\Z")


def parse_query(qstring):
    """Parse query"""
    buf = qstring[:]
    parsed = []
    while len(buf) > 0:
        for label, pattern in patterns:
            m = re.match(pattern, buf)
            if m:
                parsed.append((label, m.group()))
                buf = buf[m.end() :]
                break
        else:
            buf = buf[1:]
    return parsed


# TODO: convert a month DATE query into a RANGE: e.g. 1789-06 into 1789-06<=>1789-07


def expand_date(date, start=True):
    """Expand incomplete dates"""
    if YEAR.search(date):
        if start is True:
            date = f"{date}-01-01"
        else:
            date = f"{date}-12-31"
    if YEAR_MONTH.search(date):
        if start is True:
            date = f"{date}-01"
        else:
            date = f"{date}-31"
    return date


def parse_date_query(qstring):
    """Parse date query"""
    buf = qstring[:]
    parsed = []
    while len(buf) > 0:
        for label, pattern in date_patterns:
            m = re.match(pattern, buf)
            if m:
                date = m.group().strip()
                if label == "YEAR":
                    label = "DATE_RANGE"
                    query = f"{date}-01-01<=>{date}-12-31"
                elif label == "YEAR_MONTH":
                    label = "DATE_RANGE"
                    query = f"{date}-01<=>{date}-31"
                elif label == "DATE_RANGE":
                    start_date, end_date = date.split("<=>")
                    start_date = expand_date(start_date)
                    end_date = expand_date(end_date, start=False)
                    query = f"{start_date}<=>{end_date}"
                else:
                    query = m.group()
                parsed.append((label, query))
                buf = buf[m.end() :]
                break
        else:
            buf = buf[1:]
    return parsed


def group_terms(parsed):
    """Group terms for SQL query"""
    grouped = []
    current_clause = []
    last_term = None
    for kind, val in parsed:
        if last_term == "RANGE":
            # immediately detach ranges for now.
            grouped.append(current_clause)
            current_clause = []

        if kind == "TERM" or kind == "QUOTE" or kind == "NULL":
            if last_term != "OR" and last_term != "NOT":
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
        current_clause.append((kind, val))
        last_term = kind
    grouped.append(current_clause)
    # filter out possible empty groups
    grouped = [g for g in grouped if g != []]
    return grouped
