#!/usr/bin/env python
import urllib
from philologic.DirtyFormatter import Formatter

def hit_to_link(db,hit):
    i = 0
    partial = []
    best = []
    for n,k in enumerate(hit):
        partial.append(k)
        if partial in db.toms and db.toms[partial]["philo_name"] != "__philo_virtual":
            best = partial[:]
        else:
            break
    return "./" + "/".join(str(b) for b in best)

def make_link(query,method=None,methodarg=None,start=None,end=None,**metadata):
    q_params = [("query",query)]
    if method:
        q_params.append(("query_method",method))
    if methodarg:
        q_params.append(("query_arg",methodarg))
    q_params.extend(metadata.items()[:])
    if start:
        q_params.append(("q_start" , start))
    if end:
        q_params.append(("q_end", end))
    return "./?" + urllib.urlencode(q_params)
