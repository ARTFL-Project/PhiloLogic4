# /usr/bin/env python3
"""Report designed to group results by metadata with additional breakdown optional"""

from philologic.runtime.DB import DB

OBJ_DICT = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5, "sent": 6, "word": 7}
OBJ_ZEROS = {"doc": 6, "div1": 5, "div2": 4, "div3": 3, "para": 2, "sent": 1, "word": 0}


def aggregation_by_field(request, config):
    """Group hitlist by metadata field"""
    db = DB(config.db_path + "/data/")
    if request.q == "" and request.no_q:
        if request.no_metadata:
            hits = db.get_all(db.locals["default_object_level"], sort_order=["rowid"], raw_results=True)
        else:
            hits = db.query(sort_order=["rowid"], raw_results=True, **request.metadata)
    else:
        hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **request.metadata)

    group_by = request.group_by
    field_obj = __get_field_config(group_by, config)
    metadata_type = field_obj["object_level"]

    metadata_fields_needed = {group_by, "philo_id", f"philo_{metadata_type}_id"}
    for citation in field_obj["field_citation"]:
        if citation["field"] in db.locals["metadata_fields"]:
            metadata_fields_needed.add(citation["field"])
    if field_obj["break_up_field_citation"] is not None:
        for citation in field_obj["break_up_field_citation"]:
            if citation["field"] in db.locals["metadata_fields"]:
                metadata_fields_needed.add(citation["field"])

    hits.finish()
    philo_ids = __expand_hits(hits, metadata_type)
    cursor = db.dbh.cursor()
    # if metadata_type != "div":
    distinct_philo_ids = tuple(" ".join(map(str, id)) for id in set(philo_ids))
    cursor.execute(
        f"select {', '.join(metadata_fields_needed)} from toms where philo_{metadata_type}_id IN ({', '.join('?' for _ in range(len(distinct_philo_ids)))})",
        distinct_philo_ids,
    )
    # else:
    #     sql_query = "select * from toms where "
    #     sql_clauses = []
    #     for pos, obj_type in enumerate(["div1", "div2", "div3"]):
    #         distinct_philo_ids = tuple(" ".join(map(str, id)) for id in set(philo_ids[pos]))
    #         sql_clauses.append(f"philo_{obj_type}_id IN ({', '.join('?' for _ in range(len(distinct_philo_ids)))})")
    #     sql_query += " OR ".join(sql_clauses)
    #     cursor.execute(sql_query)

    metadata_dict = {}
    for row in cursor:
        if group_by == "title":
            uniq_name = row[f"philo_{metadata_type}_id"]
        else:
            uniq_name = row[group_by]
        metadata_dict[tuple(map(int, row[f"philo_{metadata_type}_id"].split()))] = {
            **{field: row[field] or "" for field in metadata_fields_needed if row[field] or field == group_by},
            "field_name": uniq_name,
        }

    counts_by_field = {}
    break_up_field_name = field_obj["break_up_field"]
    philo_ids_done = set()
    if break_up_field_name is not None:
        for philo_id in philo_ids:
            try:
                field_name = metadata_dict[philo_id]["field_name"]
            except KeyError:
                continue  # TODO: investigate cases if need be...
            if field_obj["break_up_field"] == "title":  # account for same title for different works
                try:
                    break_up_field = f"{metadata_dict[philo_id][break_up_field_name]} {philo_id}"
                except KeyError:
                    break_up_field = f"NO TITLE {philo_id}"
            else:
                try:
                    break_up_field = metadata_dict[philo_id][break_up_field_name]
                except KeyError:
                    break_up_field = f"NO {break_up_field_name} {philo_id}"
            if field_name not in counts_by_field:
                counts_by_field[field_name] = {
                    "count": 1,
                    "metadata_fields": metadata_dict[philo_id],
                    "break_up_field": {break_up_field: {"count": 1, "philo_id": philo_id}},
                }
            else:
                counts_by_field[field_name]["count"] += 1
                if break_up_field not in counts_by_field[field_name]["break_up_field"]:
                    philo_ids_done.add(philo_id)
                    counts_by_field[field_name]["break_up_field"][break_up_field] = {"count": 1, "philo_id": philo_id}
                else:
                    if not request.no_q and philo_id not in philo_ids_done: # we only count 1 occurrence per field for biblio searches
                        counts_by_field[field_name]["break_up_field"][break_up_field]["count"] += 1
    else:
        for philo_id in philo_ids:
            try:
                field_name = metadata_dict[philo_id]["field_name"]
            except KeyError:  # no row found in toms table
                continue
            if field_name not in counts_by_field:
                counts_by_field[field_name] = {
                    "count": 1,
                    "metadata_fields": metadata_dict[philo_id],
                    "break_up_field": {},
                }
            else:
                counts_by_field[field_name]["count"] += 1

    # del request.group_by
    if break_up_field_name is not None:
        results = []
        for field_name, values in sorted(counts_by_field.items(), key=lambda x: x[1]["count"], reverse=True):
            results.append(
                {
                    "metadata_fields": values["metadata_fields"],
                    "count": values["count"],
                    "break_up_field": [
                        {"count": v["count"], "metadata_fields": metadata_dict[v["philo_id"]]}
                        for v in sorted(values["break_up_field"].values(), key=lambda item: item["count"], reverse=True)
                    ],
                }
            )
    else:
        results = [
            {"metadata_fields": values["metadata_fields"], "count": values["count"], "break_up_field": []}
            for values in sorted(counts_by_field.values(), key=lambda x: x["count"], reverse=True)
            ]    
    
    if request.q == "" and request.no_q:
        total_results = len(philo_ids)
    else:
        total_results = len(philo_ids)    
    
    return {
        "results": results,
        "break_up_field": break_up_field_name or "",
        "query": {k: v for k, v in request},
        "total_results": total_results,
    }


def __expand_hits(hits, metadata_type):
    expanded_hits = []
    try:
        object_level = OBJ_DICT[metadata_type]
        expanded_hits = [philo_id[:object_level] for philo_id in hits]
    except KeyError:
        expanded_hits = [[] for _ in ["div1", "div2", "div3"]]
        for philo_id in hits:
            for pos, local_type in enumerate(["div1", "div2", "div3"]):
                expanded_hits[pos].append(philo_id[: OBJ_DICT[local_type]])
    return expanded_hits


def __get_field_config(group_by, config):
    for field_obj in config["stats_report_config"]:
        if field_obj["field"] == group_by:
            return field_obj


if __name__ == "__main__":
    import sys
    from philologic.runtime import WebConfig

    class Request:
        def __init__(self, q, field, metadata):
            self.q = q
            self.group_by = field
            self.no_metadata = False
            self.no_q = False
            self.metadata = metadata
            self.method = "proxy"
            self.report = "aggregation"
            self.arg = ""
            self.start = 0

        def __getitem__(self, item):
            if item == "group_by":
                return self.group_by
            return getattr(self, item)

        def __iter__(self):
            for item in ["q", "group_by", "report"]:
                yield item, self[item]

    query_term, field, db_path = sys.argv[1:]
    config = WebConfig(db_path)
    request = Request(query_term, field, {})
    aggregation_by_field(request, config)