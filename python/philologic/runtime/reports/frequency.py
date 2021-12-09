#!/usr/bin env python3
"""Frequency results for facets"""

import time
from urllib.parse import quote_plus

from philologic.runtime.DB import DB
from philologic.runtime.link import make_absolute_query_link


def frequency_results(request, config, sorted_results=False):
    """reads through a hitlist. looks up request.frequency_field in each hit, and builds up a list of
    unique values and their frequencies."""
    db = DB(config.db_path + "/data/")
    biblio_search = False
    if request.q == "" and request.no_q:
        biblio_search = True
        if request.no_metadata:
            hits = db.get_all(
                db.locals["default_object_level"],
                sort_order=["rowid"],
                raw_results=True,
            )
        else:
            hits = db.query(sort_order=["rowid"], raw_results=True, **request.metadata)
    else:
        hits = db.query(
            request["q"],
            request["method"],
            request["arg"],
            raw_results=True,
            **request.metadata,
        )

    if sorted_results is True:
        hits.finish()

    metadata_type = db.locals["metadata_types"][request.frequency_field]
    cursor = db.dbh.cursor()
    if metadata_type != "div":
        cursor.execute(
            f"SELECT philo_id, {request.frequency_field} FROM toms WHERE philo_type=? AND {request.frequency_field} IS NOT NULL",
            (metadata_type,),
        )
    else:
        cursor.execute(
            f"SELECT philo_id, {request.frequency_field} FROM toms WHERE philo_type IN (?, ?, ?) AND {request.frequency_field} IS NOT NULL",
            ("div1", "div2", "div3"),
        )
    metadata_dict = {}
    for philo_id, field_name in cursor:
        philo_id = tuple(int(s) for s in philo_id.split() if int(s))
        metadata_dict[philo_id] = field_name

    word_counts_by_field_name = db.query(get_word_count_field=request.frequency_field, **request.metadata)

    counts = {}
    frequency_object = {}
    start_time = time.perf_counter()

    obj_dict = {
        "doc": 1,
        "div1": 2,
        "div2": 3,
        "div3": 4,
        "para": 5,
        "sent": 6,
        "word": 7,
    }
    try:
        object_level = obj_dict[metadata_type]
    except KeyError:
        # metadata_type == "div"
        pass

    query_metadata = dict([(k, v) for k, v in request.metadata.items() if v])
    base_url = make_absolute_query_link(
        config,
        request,
        frequency_field="",
        start="0",
        end="0",
        report=request.report,
        script="",
    )

    hit_count = 0
    try:
        for hit_count, philo_id in enumerate(hits[request.start :]):
            if not biblio_search:
                philo_id = tuple(list(philo_id[:6]) + [philo_id[7]])
            if metadata_type == "div":
                key = ""
                for div in ["div1", "div2", "div3"]:
                    if philo_id[: obj_dict[div]] in metadata_dict:
                        key = metadata_dict[philo_id[: obj_dict[div]]]
                while not key:
                    if philo_id[:4] in metadata_dict:
                        key = metadata_dict[philo_id[:4]]
                        break
                    if philo_id[:5] in metadata_dict:
                        key = metadata_dict[philo_id[:5]]
                        break
                    break
                if not key:
                    continue
            else:
                try:
                    key = metadata_dict[philo_id[:object_level]]
                except:
                    continue
            if key not in counts:
                counts[key] = {"count": 0, "metadata": {request.frequency_field: key}}
                counts[key]["url"] = f'{base_url}&{request.frequency_field}="{quote_plus(key)}"'
                if not biblio_search:
                    try:
                        counts[key]["total_word_count"] = word_counts_by_field_name[key]
                    except KeyError:
                        # Worst case when there are different values for the field in div1, div2, and div3
                        query_metadata = {k: v for k, v in request.metadata.items() if v}
                        query_metadata[request.frequency_field] = f'"{key}"'
                        local_hits = db.query(**query_metadata)
                        counts[key]["total_word_count"] = local_hits.get_total_word_count()
            counts[key]["count"] += 1

            # avoid timeouts by splitting the query if more than
            # request.max_time (in seconds) has been spent in the loop
            # print(time.perf_counter() - start_time, hit_count, flush=True, file=sys.stderr)
            if time.perf_counter() - start_time > 5 and sorted_results is False:
                break

        hit_count += 1  # account for the fact we count from 0
        frequency_object["results"] = counts
        frequency_object["hits_done"] = request.start + hit_count
        if frequency_object["hits_done"] == len(hits):
            new_metadata = dict([(k, v) for k, v in request.metadata.items() if v])
            new_metadata[request.frequency_field] = '"NULL"'
            if request.q == "" and request.no_q:
                new_hits = db.query(sort_order=["rowid"], raw_results=True, **new_metadata)
            else:
                new_hits = db.query(
                    request["q"],
                    request["method"],
                    request["arg"],
                    raw_results=True,
                    **new_metadata,
                )
            new_hits.finish()
            if len(new_hits):
                null_url = f'{base_url}&{request.frequency_field}="NULL"'
                local_hits = db.query(**new_metadata, raw_results=True)
                if not biblio_search:
                    frequency_object["results"]["NULL"] = {
                        "count": len(new_hits),
                        "url": null_url,
                        "metadata": {request.frequency_field: '"NULL"'},
                        "total_word_count": local_hits.get_total_word_count(),
                    }
                else:
                    frequency_object["results"]["NULL"] = {
                        "count": len(new_hits),
                        "url": null_url,
                        "metadata": {request.frequency_field: '"NULL"'},
                    }
            frequency_object["more_results"] = False
        else:
            frequency_object["more_results"] = True
    except IndexError:
        frequency_object["results"] = {}
        frequency_object["more_results"] = False
    frequency_object["results_length"] = len(hits)
    frequency_object["query"] = dict([i for i in request])

    if sorted_results is True:
        frequency_object["results"] = sorted(
            frequency_object["results"].items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        )

    return frequency_object


if __name__ == "__main__":
    import sys
    from philologic.runtime import WebConfig

    class Request:
        def __init__(self, q, field, metadata):
            self.q = q
            self.frequency_field = field
            self.no_metadata = False
            self.no_q = False
            self.metadata = metadata
            self.method = "proxy"
            self.report = "frequency"
            self.arg = ""
            self.start = 0

        def __getitem__(self, item):
            return getattr(self, item)

        def __iter__(self):
            for item in ["q", "frequency_field", "report"]:
                yield item, self[item]

    query_term, field, db_path = sys.argv[1:]
    config = WebConfig(db_path)
    request = Request(query_term, field, {})
    frequency_results(request, config)
