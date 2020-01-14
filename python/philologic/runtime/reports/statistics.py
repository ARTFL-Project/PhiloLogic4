# /usr/bin/env python3

from philologic.runtime.DB import DB
from philologic.runtime.link import make_absolute_query_link


OBJ_DICT = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5, "sent": 6, "word": 7}
OBJ_ZEROS = {"doc": 6, "div1": 5, "div2": 4, "div3": 3, "para": 2, "sent": 1, "word": 0}


def statistics_by_field(request, config):
    db = DB(config.db_path + "/data/")
    biblio_search = False
    if request.q == "" and request.no_q:
        biblio_search = True
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
    for philo_id in philo_ids:
        field_name = metadata_dict[philo_id][request.group_by]
        if field_name not in counts_by_field:
            counts_by_field[field_name] = {"count": 1, "metadata_fields": metadata_dict[philo_id]}
        else:
            counts_by_field[field_name]["count"] += 1

    counts_by_field = sorted(counts_by_field.items(), key=lambda x: x[1]["count"], reverse=True)
    citations = config["bibliography_citation"]
    citation_pos = __get_field_pos(citations, request.group_by)
    if citation_pos is not None:
        field_citation = citations.pop(citation_pos)
        field_citation["link"] = True
    else:
        field_citation = {
            "style": {"font-variant": "small-caps"},
            "suffix": "",
            "object_level": "doc",
            "field": "author",
            "prefix": "",
            "link": True,
            "separator": ",",
        }
    results = []
    group_by_field = request.group_by
    del request.group_by
    for field_name, values in counts_by_field:
        quoted_field = f'"{field_name}"'
        link = f"""concordance?{make_absolute_query_link(config, request, script_name="", **{group_by_field :quoted_field})}"""
        result_citation = [{**field_citation, "href": link, "label": field_name}, *__build_citation(values, citations)]
        results.append({"citation": result_citation, "count": values["count"]})

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


def __get_field_pos(citations, field):
    for pos, citation in enumerate(citations):
        if citation["field"] == field:
            return pos
    return None


def __build_citation(values, citation_object):
    citations = []
    for citation in citation_object:
        try:
            label = values["metadata_fields"][citation["field"]]
        except KeyError:
            continue
        citations.append({"label": label, "href": "", **citation})
    return citations
