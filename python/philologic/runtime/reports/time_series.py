#!/usr/bin/env python3
"""Time series"""

import regex as re
import timeit
from collections import defaultdict

from philologic.runtime.link import make_absolute_query_link
from philologic.runtime.DB import DB


def generate_time_series(request, config):
    db = DB(config.db_path + "/data/")
    time_series_object = {"query": dict([i for i in request]), "query_done": False}

    # Invalid date range
    if request.start_date == "invalid" or request.end_date == "invalid":
        time_series_object["results_length"] = 0
        time_series_object["more_results"] = False
        time_series_object["new_start_date"] = 0
        time_series_object["results"] = {"absolute_count": {}, "date_count": {}}
        return time_series_object

    start_date, end_date = get_start_end_date(
        db, config, start_date=request.start_date or None, end_date=request.end_date or None
    )

    # Generate date ranges
    interval = int(request.year_interval)
    date_ranges = []
    # Make sure last date gets included in for loop below by adding one to last step
    for start in range(start_date, end_date + 1, interval):
        end = start + interval - 1
        if end > end_date:
            end = end_date
        date_range = "%d-%d" % (start, end)
        date_ranges.append((start, date_range))

    absolute_count = defaultdict(int)
    date_counts = {}
    total_hits = 0
    last_date_done = start_date
    start_time = timeit.default_timer()
    max_time = request.max_time or 10
    cursor = db.dbh.cursor()
    for start_range, date_range in date_ranges:
        request.metadata[config.time_series_year_field] = date_range
        hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **request.metadata)
        hits.finish()
        hit_len = len(hits)
        params = {"report": "concordance", "start": "0", "end": "0"}
        params[config.time_series_year_field] = date_range
        url = make_absolute_query_link(config, request, **params)
        absolute_count[str(start_range)] = {"label": start_range, "count": hit_len, "url": url}

        # Get date total count
        if interval != 1:
            end_range = start_range + (int(request["year_interval"]) - 1)
            if request.q:
                query = f'select sum(word_count) from toms where {config.time_series_year_field} between "{start_range}" and "{end_range}"'
            else:
                query = f"SELECT COUNT(*) FROM toms WHERE philo_type='{db.locals.default_object_level}' AND {config.time_series_year_field} BETWEEN {start_range} AND {end_range}"
        else:
            if request.q:
                query = f"select sum(word_count) from toms where {config.time_series_year_field}='{start_range}'"
            else:
                query = f"SELECT COUNT(*) FROM toms WHERE philo_type='{db.locals.default_object_level}' AND {config.time_series_year_field}='{start_range}'"
        cursor.execute(query)
        date_counts[start_range] = cursor.fetchone()[0] or 0
        total_hits += hit_len
        elapsed = timeit.default_timer() - start_time
        last_date_done = start_range
        # avoid timeouts by splitting the query if more than request.max_time
        # (in seconds) has been spent in the loop
        if elapsed > int(max_time):
            break

    time_series_object["results_length"] = total_hits
    if (last_date_done + int(request.year_interval)) >= end_date:
        time_series_object["more_results"] = False
    else:
        time_series_object["more_results"] = True
        time_series_object["new_start_date"] = last_date_done + int(request.year_interval)
    time_series_object["results"] = {
        "absolute_count": absolute_count,
        "date_count": {str(date): count for date, count in date_counts.items()},
    }

    return time_series_object


def get_start_end_date(db, config, start_date=None, end_date=None):
    """Get start and end date of dataset"""
    date_finder = re.compile(r"^.*?(\d{1,}).*")
    cursor = db.dbh.cursor()
    object_type = db.locals["metadata_types"][config.time_series_year_field]
    if object_type == "div":
        year_field_type = ("div1", "div2", "div3")
    else:
        year_field_type = (object_type,)
    cursor.execute(
        f"select {config.time_series_year_field} from toms where {config.time_series_year_field} is not null AND philo_type IN ({','.join('?' for _ in range(len(year_field_type)))})",
        year_field_type,
    )
    dates = []
    for i in cursor:
        try:
            dates.append(int(i[0]))
        except:
            date_match = date_finder.search(i[0])
            if date_match:
                dates.append(int(date_match.groups()[0]))
            else:
                pass
    min_date = min(dates)
    if not start_date:
        start_date = min_date
    max_date = max(dates)
    if not end_date:
        end_date = max_date
    return start_date, end_date
