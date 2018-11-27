#!/usr/bin/env python3
"""Filter word by property
Currently unmaintained"""

from philologic.runtime.citations import citation_links, citations
from philologic.runtime.get_text import get_concordance_text
from philologic.runtime.reports.generate_word_frequency import get_word_attrib
from philologic.DB import DB


def filter_words_by_property(request, config):
    """Filter words by property"""
    db = DB(config.db_path + "/data/")
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    concordance_object = {"query": dict([i for i in request])}

    # Do these need to be captured in wsgi_handler?
    word_property = request["word_property"]
    word_property_value = request["word_property_value"]
    word_property_total = request["word_property_total"]

    new_hitlist = []
    results = []
    position = 0
    more_pages = False

    if request.start == 0:
        start = 1
    else:
        start = request.start

    for hit in hits:
        # get my chunk of text
        hit_val = get_word_attrib(hit, word_property, db)

        if hit_val == word_property_value:
            position += 1
            if position < start:
                continue
            new_hitlist.append(hit)
            citation_hrefs = citation_links(db, config, hit)
            metadata_fields = {}
            for metadata in db.locals["metadata_fields"]:
                metadata_fields[metadata] = hit[metadata]
            citation = citations(hit, citation_hrefs, config)
            context = get_concordance_text(db, hit, config.db_path, config.concordance_length)
            result_obj = {
                "philo_id": hit.philo_id,
                "citation": citation,
                "citation_links": citation_hrefs,
                "context": context,
                "metadata_fields": metadata_fields,
                "bytes": hit.bytes,
                "collocate_count": 1,
            }
            results.append(result_obj)

        if len(new_hitlist) == (request.results_per_page):
            more_pages = True
            break

    end = start + len(results) - 1
    if len(results) < request.results_per_page:
        word_property_total = end
    else:
        word_property_total = end + 1
    concordance_object["results"] = results
    concordance_object["query_done"] = hits.done
    concordance_object["results_length"] = word_property_total
    concordance_object["description"] = {
        "start": start,
        "end": end,
        "results_per_page": request.results_per_page,
        "more_pages": more_pages,
    }
    return concordance_object
