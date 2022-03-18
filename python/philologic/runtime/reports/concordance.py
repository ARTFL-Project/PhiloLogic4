#!/usr/bin/env python3
"""Concordance report"""

import regex as re
from philologic.runtime.pages import page_interval
from philologic.runtime.citations import citations, citation_links
from philologic.runtime.get_text import get_concordance_text
from philologic.runtime.DB import DB
from philologic.runtime.HitList import CombinedHitlist


def concordance_results(request, config):
    """Fetch concordances results."""
    db = DB(config.db_path + "/data/")
    if request.collocation_type:
        first_hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
        second_hits = db.query(request["left"], request["method"], request["arg"], **request.metadata)
        hits = CombinedHitlist(first_hits, second_hits)
    else:
        hits = db.query(
            request["q"],
            request["method"],
            request["arg"],
            sort_order=request["sort_order"],
            ascii_sort=db.locals.ascii_conversion,
            **request.metadata,
        )
    start, end, _ = page_interval(request["results_per_page"], hits, request.start, request.end)

    concordance_object = {
        "description": {"start": start, "end": end, "results_per_page": request.results_per_page},
        "query": dict([i for i in request]),
        "default_object": db.locals["default_object_level"],
    }

    formatting_regexes = []
    if config.concordance_formatting_regex:
        for pattern, replacement in config.concordance_formatting_regex:
            compiled_regex = re.compile(rf"{pattern}")
            formatting_regexes.append((compiled_regex, replacement))
    results = []
    for hit in hits[start - 1 : end]:
        citation_hrefs = citation_links(db, config, hit)
        metadata_fields = {metadata: hit[metadata] for metadata in db.locals["metadata_fields"]}
        citation = citations(hit, citation_hrefs, config, report="concordance")
        context = get_concordance_text(db, hit, config.db_path, config.concordance_length)
        if formatting_regexes:
            for formatting_regex, replacement in formatting_regexes:
                context = formatting_regex.sub(rf"{replacement}", context)
        result_obj = {
            "philo_id": hit.philo_id,
            "citation": citation,
            "citation_links": citation_hrefs,
            "context": context,
            "metadata_fields": metadata_fields,
            "bytes": hit.bytes,
        }
        results.append(result_obj)
    concordance_object["results"] = results
    concordance_object["results_length"] = len(hits)
    concordance_object["query_done"] = hits.done
    return concordance_object
