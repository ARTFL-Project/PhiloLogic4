#!/usr/bin/env python
"""Page intervals"""

def page_interval(num, results, start, end):
    """Return page intervals"""
    start = int(start)
    end = int(end)
    num = int(num)
    if start <= 0:
        start = 1
    if end <= 0:
        end = start + (num - 1)
    results_len = len(results)
    if end > results_len and results.done:
        end = results_len
    n = start - 1
    return start, end, n