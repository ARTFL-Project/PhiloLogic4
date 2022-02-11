#!/usr/bin/env python3
"""KWIC results"""


import regex as re
from philologic.runtime.citations import citation_links, citations
from philologic.runtime.get_text import get_text
from philologic.runtime.ObjectFormatter import adjust_bytes, format_strip
from philologic.runtime.pages import page_interval
from philologic.runtime.DB import DB


def kwic_results(request, config):
    """Fetch KWIC results"""
    db = DB(config.db_path + "/data/")
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    start, end, n = page_interval(request.results_per_page, hits, request.start, request.end)
    kwic_object = {
        "description": {"start": start, "end": end, "results_per_page": request.results_per_page},
        "query": dict([i for i in request]),
    }
    kwic_object["results"] = []

    for hit in hits[start - 1 : end]:
        kwic_result = kwic_hit_object(hit, config, db)
        kwic_object["results"].append(kwic_result)

    kwic_object["results_length"] = len(hits)
    kwic_object["query_done"] = hits.done

    return kwic_object


def kwic_hit_object(hit, config, db):
    """Build an individual kwic concordance"""
    # Get all metadata
    metadata_fields = {}
    for metadata in db.locals["metadata_fields"]:
        metadata_fields[metadata] = f"{hit[metadata]}".strip()

    # Get all links and citations
    citation_hrefs = citation_links(db, config, hit)
    citation = citations(hit, citation_hrefs, config)

    # Determine length of text needed
    byte_distance = hit.bytes[-1] - hit.bytes[0]
    length = config.concordance_length + byte_distance + config.concordance_length

    # Get concordance and align it
    byte_offsets, start_byte = adjust_bytes(hit.bytes, config.concordance_length)
    conc_text = get_text(hit, start_byte, length, config.db_path)
    conc_text = format_strip(conc_text, db.locals["token_regex"], byte_offsets)
    conc_text = conc_text.replace("\n", " ")
    conc_text = conc_text.replace("\r", "")
    conc_text = conc_text.replace("\t", " ")
    try:
        start_hit = conc_text.index('<span class="highlight">')
        start_output = (
            '<span class="kwic-before"><span class="inner-before">' + conc_text[:start_hit] + "</span></span>"
        )
        end_hit = conc_text.rindex("</span>") + 7
        highlighted_text = conc_text[start_hit + 23 : end_hit - 7].lower()  # for use in KWIC sorting
        end_output = '<span class="kwic-after">' + conc_text[end_hit:] + "</span>"
        conc_text = (
            '<span class="kwic-text">'
            + start_output
            + '&nbsp;<span class="kwic-highlight">'
            + conc_text[start_hit:end_hit]
            + "</span>&nbsp;"
            + end_output
            + "</span>"
        )
    except ValueError as v:
        import sys

        print("KWIC ERROR:", v, file=sys.stderr)

    if config.kwic_formatting_regex:
        for pattern, replacement in config.kwic_formatting_regex:
            conc_text = re.sub(r"%s" % pattern, "%s" % replacement, conc_text)
    kwic_result = {
        "philo_id": hit.philo_id,
        "context": conc_text,
        "highlighted_text": highlighted_text,
        "metadata_fields": metadata_fields,
        "citation_links": citation_hrefs,
        "citation": citation,
        "bytes": hit.bytes,
    }

    return kwic_result
