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
            hits = db.get_all(db.locals["default_object_level"], sort_order=["rowid"], raw_results=True,)
        else:
            hits = db.query(sort_order=["rowid"], raw_results=True, **request.metadata)
    else:
        hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **request.metadata,)

    if sorted_results is True:
        hits.finish()

    cursor = db.dbh.cursor()

    cursor.execute(f"SELECT philo_id, {request.frequency_field} FROM toms WHERE {request.frequency_field} IS NOT NULL")
    metadata_dict = {}
    for i in cursor:
        philo_id, field = i
        philo_id = tuple(int(s) for s in philo_id.split() if int(s))
        metadata_dict[philo_id] = field

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
    metadata_type = db.locals["metadata_types"][request.frequency_field]
    try:
        object_level = obj_dict[metadata_type]
    except KeyError:
        # metadata_type == "div"
        pass

    query_metadata = dict([(k, v) for k, v in request.metadata.items() if v])
    base_url = make_absolute_query_link(
        config, request, frequency_field="", start="0", end="0", report=request.report, script="",
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
                    query_metadata[request.frequency_field] = f'"{key}"'
                    local_hits = db.query(**query_metadata, raw_results=True)
                    counts[key]["total_word_count"] = local_hits.get_total_word_count()
            counts[key]["count"] += 1

            # avoid timeouts by splitting the query if more than
            # request.max_time (in seconds) has been spent in the loop
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
                new_hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **new_metadata,)
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
            frequency_object["results"].items(), key=lambda x: x[1]["count"], reverse=True,
        )

    return frequency_object


# #!/usr/bin env python3
# """Frequency results for facets"""

# import timeit

# from philologic.runtime.link import make_absolute_query_link
# from philologic.runtime.DB import DB

# OBJ_DICT = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5, "sent": 6, "word": 7}


# def frequency_results(request, config, sorted_results=False):
#     """reads through a hitlist. looks up request.frequency_field in each hit, and builds up a list of
#        unique values and their frequencies."""
#     db = DB(config.db_path + "/data/")
#     biblio_search = False
#     if request.q == "" and request.no_q:
#         biblio_search = True
#         if request.no_metadata:
#             hits = db.get_all(
#                 db.locals["default_object_level"],
#                 sort_order=["rowid"],
#                 raw_results=True,
#             )
#         else:
#             hits = db.query(sort_order=["rowid"], raw_results=True, **request.metadata)
#     else:
#         hits = db.query(
#             request["q"],
#             request["method"],
#             request["arg"],
#             raw_results=True,
#             **request.metadata,
#         )

#     metadata_type = db.locals["metadata_types"][request.frequency_field]
#     try:
#         object_level = OBJ_DICT[metadata_type]
#     except KeyError:
#         metadata_type == "div"

#     hits.finish()
#     philo_ids, last_hit_done = __expand_hits(
#         hits, metadata_type, request, sorted_results
#     )
#     import sys

#     print(last_hit_done, file=sys.stderr)

#     cursor = db.dbh.cursor()
#     if metadata_type != "div":
#         distinct_philo_ids = tuple(" ".join(map(str, id)) for id in set(philo_ids))
#         cursor.execute(
#             f"select philo_id, philo_type, {request.frequency_field} from toms where philo_{metadata_type}_id IN ({', '.join('?' for _ in range(len(distinct_philo_ids)))})",
#             distinct_philo_ids,
#         )
#     else:
#         sql_query = (
#             f"select philo_id, philo_type, {request.frequency_field} from toms where "
#         )
#         sql_clauses = []
#         for pos, obj_type in enumerate(["div1", "div2", "div3"]):
#             distinct_philo_ids = tuple(
#                 " ".join(map(str, id)) for id in set(philo_ids[pos])
#             )
#             sql_clauses.append(
#                 f"philo_{obj_type}_id IN ({', '.join('?' for _ in range(len(distinct_philo_ids)))})"
#             )
#         sql_clauses = " OR ".join(sql_clauses)
#         cursor.execute(sql_query)

#     metadata_dict = {
#         tuple(map(int, row["philo_id"].split()[: OBJ_DICT[row["philo_type"]]])): row[
#             request.frequency_field
#         ]
#         for row in cursor
#     }

#     counts = {}
#     frequency_object = {}
#     query_metadata = dict([(k, v) for k, v in request.metadata.items() if v])
#     base_url = make_absolute_query_link(
#         config,
#         request,
#         frequency_field="",
#         start="0",
#         end="0",
#         report=request.report,
#         script="",
#     )

#     try:
#         for philo_id in philo_ids[request.start :]:
#             try:
#                 key = metadata_dict[philo_id[:object_level]] or ""
#             except:
#                 last_hit_done += 1
#                 continue
#             if key not in counts:
#                 counts[key] = {"count": 0, "metadata": {request.frequency_field: key}}
#                 counts[key]["url"] = f'{base_url}&{request.frequency_field}="{key}"'
#                 if not biblio_search:
#                     query_metadata[request.frequency_field] = '"%s"' % key
#                     local_hits = db.query(**query_metadata, raw_results=True)
#                     counts[key]["total_word_count"] = local_hits.get_total_word_count()
#             counts[key]["count"] += 1

#             # avoid timeouts by splitting the query if more than
#             # request.max_time (in seconds) has been spent in the loop
#             # elapsed = timeit.default_timer() - start_time
#             # last_hit_done += 1
#             # if elapsed > 5 and sorted_results is False:
#             #     break

#         frequency_object["results"] = counts
#         frequency_object["hits_done"] = last_hit_done
#         if last_hit_done == len(hits):
#             new_metadata = dict([(k, v) for k, v in request.metadata.items() if v])
#             new_metadata[request.frequency_field] = '"NULL"'
#             if request.q == "" and request.no_q:
#                 new_hits = db.query(
#                     sort_order=["rowid"], raw_results=True, **new_metadata
#                 )
#             else:
#                 new_hits = db.query(
#                     request["q"],
#                     request["method"],
#                     request["arg"],
#                     raw_results=True,
#                     **new_metadata,
#                 )
#             new_hits.finish()
#             if len(new_hits):
#                 null_url = f'{base_url}&{request.frequency_field}="NULL"'
#                 local_hits = db.query(**new_metadata, raw_results=True)
#                 if not biblio_search:
#                     frequency_object["results"]["NULL"] = {
#                         "count": len(new_hits),
#                         "url": null_url,
#                         "metadata": {request.frequency_field: '"NULL"'},
#                         "total_word_count": local_hits.get_total_word_count(),
#                     }
#                 else:
#                     frequency_object["results"]["NULL"] = {
#                         "count": len(new_hits),
#                         "url": null_url,
#                         "metadata": {request.frequency_field: '"NULL"'},
#                     }
#             frequency_object["more_results"] = False
#         else:
#             frequency_object["more_results"] = True
#     except IndexError as e:
#         import sys

#         print(e, file=sys.stderr)
#         frequency_object["results"] = {}
#         frequency_object["more_results"] = False
#     frequency_object["results_length"] = len(hits)
#     frequency_object["query"] = dict([i for i in request])

#     if sorted_results is True:
#         frequency_object["results"] = sorted(
#             frequency_object["results"].items(),
#             key=lambda x: x[1]["count"],
#             reverse=True,
#         )

#     return frequency_object


# def __expand_hits(hits, metadata_type, request, sorted_results):
#     start_time = timeit.default_timer()
#     last_hit_done = request.start
#     expanded_hits = []
#     # import sys

#     try:
#         object_level = OBJ_DICT[metadata_type]
#         append = expanded_hits.append
#         for philo_id in hits[request.start :]:
#             append(philo_id[:object_level])
#             # avoid timeouts by splitting the query if more than
#             # request.max_time (in seconds) has been spent in the loop
#             elapsed = timeit.default_timer() - start_time
#             # print(elapsed, file=sys.stderr)
#             last_hit_done += 1
#             if elapsed > 5 and sorted_results is False:
#                 break
#         expanded_hits = [philo_id[:object_level] for philo_id in hits[request.start :]]
#     except KeyError:
#         expanded_hits = [[] for _ in ["div1", "div2", "div3"]]
#         for philo_id in hits:
#             for pos, local_type in enumerate(["div1", "div2", "div3"]):
#                 expanded_hits[pos].append(philo_id[: OBJ_DICT[local_type]])
#     return expanded_hits, last_hit_done
