#!/usr/bin/env python
"""Citations"""

from __future__ import absolute_import, print_function
from philologic.runtime.link import (make_absolute_object_link, make_absolute_query_link)
import six


def citation_links(db, config, i):
    """ Returns links to a PhiloLogic object and all its ancestors."""
    doc_href = make_absolute_object_link(config, i.philo_id[:1]) + '/table-of-contents'
    div1_href = make_absolute_object_link(config, i.philo_id[:2], i.bytes)
    div2_href = make_absolute_object_link(config, i.philo_id[:3], i.bytes)
    div3_href = make_absolute_object_link(config, i.philo_id[:4], i.bytes)
    page_href = make_absolute_object_link(config, i.page.philo_id, i.bytes)
    try:
        line_href = make_absolute_object_link(config, i.line.philo_id, i.bytes)
    except AttributeError:
        line_href = ""

    links = {"doc": doc_href, "div1": div1_href, "div2": div2_href, "div3": div3_href,
             "para": "", "page": page_href, "line": line_href}

    for field, metadata_type in six.iteritems(db.locals["metadata_types"]):
        if metadata_type == 'para':
            links['para'] = make_absolute_object_link(config, i.philo_id[:5], i.bytes)
            break
    return links


def citations(hit, citation_hrefs, config, report="concordance", citation_type=None, result_type="doc"):
    """ Returns a representation of a PhiloLogic object and all its ancestors
        suitable for a precise citation. """
    if citation_type is None:
        citation_type = config[report + "_citation"]
    citation = []
    for pos, citation_object in enumerate(citation_type):
        cite = {}
        cite["label"] = get_label(hit, citation_object)
        if cite["label"]:
            cite["prefix"] = citation_object["prefix"]
            cite["suffix"] = citation_object["suffix"]
            cite["separator"] = citation_object["separator"]
            cite["href"] = cite_linker(hit, citation_object, citation_hrefs, config, report)
            cite["style"] = citation_object["style"]
            cite["object_type"] = citation_object["object_level"]
            citation.append(cite)
    return citation


def get_label(hit, citation_object):
    """Get metadata labels"""
    label = ""
    if citation_object["object_level"] == "doc":
        label = hit[citation_object["field"]].strip()
    if citation_object["object_level"].startswith("div"):
        if citation_object["field"] == "head":
            if citation_object["object_level"] == "div1":
                label = get_div1_name(hit)
                if label == "Text" and hit.div1.philo_id[-1] == 0:  # This is a fake div1 of id 0
                    label = ""
            else:
                div1_name = get_div1_name(hit)
                div2_name = hit.div2.head.strip()
                div3_name = hit.div3.head.strip()
                if div3_name == div2_name and hit.div3.philo_id[-1] == 0:
                    div3_name = ''
                if div2_name == div1_name and hit.div2.philo_id[-1] == 0:
                    div2_name = ''
                if citation_object["object_level"] == "div2":
                    label = div2_name
                else:
                    label = div3_name
        else:
            label = hit[citation_object["object_level"]][citation_object["field"]].strip()
        if label == "[NA]":
            if citation_object["object_level"] == "div1":
                label = "Section"
            else:
                label = "Subsection"
    elif citation_object["object_level"] == "para":
        label = hit[citation_object["field"]].strip().title()
    elif citation_object["object_level"] == "page":
        page_num = hit.page[citation_object["field"]]
        if page_num:
            try:
                label = str(page_num)
            except UnicodeEncodeError:
                label = page_num.encode('utf-8', 'ignore')  # page number is a unicode char
    elif citation_object["object_level"] == "line":
        try:
            line = hit.line[citation_object["field"]].strip()
            if line:
                label = "line %s" % str(line)
        except TypeError:
            pass
    return label


def get_div1_name(hit):
    """Get div1 names"""
    label = hit.div1.head
    if not label:
        if hit.div1.philo_name == "__philo_virtual":
            label = "Section"
        else:
            if hit.div1["type"] and hit.div1["n"]:
                label = hit.div1['type'] + " " + hit.div1["n"]
            else:
                label = hit.div1["head"] or hit.div1['type'] or hit.div1['philo_name'] or hit.div1['philo_type']
    try:
        label = label[0].upper() + label[1:]
        label = label.strip()
    except IndexError:
        pass
    return label


def cite_linker(hit, citation_object, citation_hrefs, config, report):
    """Get links"""
    href = None
    if citation_object["link"]:
        if citation_object["object_level"] == "doc":
            if citation_object["field"] == "title" or citation_object["field"] == "filename":
                href = citation_hrefs['doc']
            elif report == "bibliography" and citation_object["field"] == "head":
                href = make_absolute_object_link(config, hit.philo_id)
            else:
                params = [("report", "bibliography"),
                          (citation_object["field"], '"%s"' % hit[citation_object["field"]])]
                href = make_absolute_query_link(config, params)
        else:
            href = citation_hrefs[citation_object["object_level"]]
    return href
