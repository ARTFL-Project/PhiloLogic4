# /usr/bin/env python3
"""Report designed to group results by metadata with additional breakdown optional"""

from philologic.runtime.DB import DB
from philologic.runtime.link import make_absolute_query_link


OBJ_DICT = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5, "sent": 6, "word": 7}
OBJ_ZEROS = {"doc": 6, "div1": 5, "div2": 4, "div3": 3, "para": 2, "sent": 1, "word": 0}


def statistics_by_field(request, config):
    """Group hitlist by metadata field"""
    db = DB(config.db_path + "/data/")
    if request.q == "" and request.no_q:
        if request.no_metadata:
            hits = db.get_all(db.locals["default_object_level"], sort_order=["rowid"], raw_results=True)
        else:
            hits = db.query(sort_order=["rowid"], raw_results=True, **request.metadata)
    else:
        hits = db.query(request["q"], request["method"], request["arg"], raw_results=True, **request.metadata)

    metadata_type = db.locals["metadata_types"][request.group_by]

    hits.finish()
    philo_ids = __expand_hits(hits, metadata_type)
    distinct_philo_ids = tuple(set(philo_ids))
    cursor = db.dbh.cursor()
    cursor.execute(
        f"select * from toms where philo_id IN ({', '.join('?' for _ in range(len(distinct_philo_ids)))})",
        distinct_philo_ids,
    )
    metadata_dict = {}
    for row in cursor:
        metadata_dict[row["philo_id"]] = {field: row[field] for field in db.locals["metadata_fields"]}

    counts_by_field = {}
    field_obj = __get_field_config(request, config)
    break_up_field_name = field_obj["break_up_field"]
    for philo_id in philo_ids:
        field_name = metadata_dict[philo_id][request.group_by]
        break_up_field = metadata_dict[philo_id][break_up_field_name]
        if field_name not in counts_by_field:
            counts_by_field[field_name] = {
                "count": 1,
                "metadata_fields": metadata_dict[philo_id],
                "break_up_field": {break_up_field: {"count": 1, "philo_id": philo_id}},
            }
        else:
            counts_by_field[field_name]["count"] += 1
            if break_up_field not in counts_by_field[field_name]["break_up_field"]:
                counts_by_field[field_name]["break_up_field"][break_up_field] = {"count": 1, "philo_id": philo_id}
            else:
                counts_by_field[field_name]["break_up_field"][break_up_field]["count"] += 1

    counts_by_field = sorted(counts_by_field.items(), key=lambda x: x[1]["count"], reverse=True)
    results = []
    group_by_field = request.group_by
    del request.group_by
    for field_name, values in counts_by_field:
        result_citation = __build_citation(
            values["metadata_fields"], field_obj["field_citation"], group_by_field, config, request
        )

        results.append(
            {
                "citation": result_citation,
                "count": values["count"],
                "break_up_field": [
                    {
                        "count": v["count"],
                        "citation": __build_citation(
                            metadata_dict[v["philo_id"]],
                            field_obj["break_up_field_citation"],
                            break_up_field_name,
                            config,
                            request,
                        ),
                    }
                    for k, v in sorted(
                        values["break_up_field"].items(), key=lambda item: item[1]["count"], reverse=True
                    )
                ],
            }
        )

    return {"results": results, "query": dict([i for i in request])}


def __expand_hits(hits, metadata_type):
    try:
        object_level = OBJ_DICT[metadata_type]
    except KeyError:
        # metadata_type == "div"
        pass
    expanded_hits = []
    for philo_id in hits:
        if metadata_type == "div":
            for local_type in ["div1", "div2", "div3"]:
                local_id = " ".join(str(i) for i in philo_id[: OBJ_DICT[local_type]])
                expanded_hits.append(f"""{local_id} {' '.join("0" for _ in range(OBJ_ZEROS[local_type]))}""")
        else:
            local_id = " ".join(str(i) for i in philo_id[:object_level])
            expanded_hits.append(f"""{local_id} {' '.join("0" for _ in range(OBJ_ZEROS[metadata_type]))}""")
    return expanded_hits


def __get_field_config(request, config):
    for field_obj in config["stats_report_config"]["fields"]:
        if field_obj["field"] == request.group_by:
            return field_obj


def __build_citation(metadata_fields, citation_object, field_to_link, config, request):
    citations = []
    for citation in citation_object:
        try:
            label = metadata_fields[citation["field"]]
        except KeyError:
            continue
        if not label:
            continue
        if citation["field"] == field_to_link:
            quoted_field = f'"{label}"'
            link = f"""concordance?{make_absolute_query_link(config, request, script_name="", **{field_to_link :quoted_field})}"""
            citations.append({"label": label, "href": link, **citation})
        else:
            citations.append({"label": label, "href": "", **citation})
    return citations
