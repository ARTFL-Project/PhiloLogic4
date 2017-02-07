#!/usr/bin/env python3
"""Concordance report"""

import re

from philologic.runtime.pages import page_interval
from philologic.runtime.citations import citations, citation_links
from philologic.runtime.get_text import get_concordance_text
from philologic.DB import DB
from philologic.HitList import CombinedHitlist


def concordance_results(request, config):
    """Fetch concordances results."""
    db = DB(config.db_path + '/data/')
    if request.collocation_type:
        first_hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
        second_hits = db.query(request["left"], request["method"], request["arg"], **request.metadata)
        hits = CombinedHitlist(first_hits, second_hits)
    else:
        hits = db.query(request["q"],
                        request["method"],
                        request["arg"],
                        sort_order=request["sort_order"],
                        **request.metadata)
    start, end, page_num = page_interval(request['results_per_page'], hits, request.start, request.end)

    concordance_object = {
        "description": {"start": start,
                        "end": end,
                        "results_per_page": request.results_per_page},
        "query": dict([i for i in request]),
        "default_object": db.locals['default_object_level']
    }

    formatting_regexes = []
    if config.concordance_formatting_regex:
        for pattern, replacement in config.concordance_formatting_regex:
            compiled_regex = re.compile(r'%s' % pattern)
            formatting_regexes.append((compiled_regex, replacement))
    results = []
    for hit in hits[start - 1:end]:
        import sys
        print("FILE", hit.hit, hit.filename, file=sys.stderr)
        citation_hrefs = citation_links(db, config, hit)
        metadata_fields = {}
        for metadata in db.locals['metadata_fields']:
            metadata_fields[metadata] = hit[metadata]
        citation = citations(hit, citation_hrefs, config, report="concordance")
        context = get_concordance_text(db, hit, config.db_path, config.concordance_length)
        if formatting_regexes:
            for formatting_regex, replacement in formatting_regexes:
                context = formatting_regex.sub(r'%s' % replacement, context)
        result_obj = {
            "philo_id": hit.philo_id,
            "citation": citation,
            "citation_links": citation_hrefs,
            "context": context,
            "metadata_fields": metadata_fields,
            "bytes": hit.bytes
        }
        results.append(result_obj)
    concordance_object["results"] = results
    concordance_object['results_length'] = len(hits)
    concordance_object["query_done"] = hits.done
    return concordance_object
