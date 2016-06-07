#!/usr/bin/env python

from link import *


def citation_links(db, config, i):
    """ Returns a representation of a PhiloLogic object and all its ancestors
        suitable for a precise concordance citation. """
    doc_href = make_absolute_object_link(config, i.philo_id[:1]) + '/table-of-contents'
    div1_href = make_absolute_object_link(config, i.philo_id[:2], i.bytes)
    div2_href = make_absolute_object_link(config, i.philo_id[:3], i.bytes)
    div3_href = make_absolute_object_link(config, i.philo_id[:4], i.bytes)
    page_href = make_absolute_object_link(config, i.page.philo_id, i.bytes)

    links = {"doc": doc_href, "div1": div1_href, "div2": div2_href, "div3": div3_href, "page": page_href}

    try:
        speaker_name = i.para.who
        if speaker_name:
            links['para'] = make_absolute_object_link(config, i.philo_id[:5], i.bytes)
    except AttributeError:
        links["para"] = ""
    return links


def concordance_citation(hit, citation_hrefs):
    """ Returns a representation of a PhiloLogic object and all its ancestors
        suitable for a precise concordance citation. """

    citation = {}

    ## Doc level metadata
    citation['title'] = {"href": citation_hrefs['doc'], "label": hit.title.strip()}
    if hit.author:
        citation['author'] = {"href": citation_hrefs['doc'], "label": hit.author.strip()}
    else:
        citation['author'] = {}
    if hit.year:
        citation['year'] = {"href": citation_hrefs['doc'], "label": hit.year.strip()}
    else:
        citation['year'] = {}

    ## Div level metadata
    div1_name = hit.div1.head
    if not div1_name:
        if hit.div1.philo_name == "__philo_virtual":
            div1_name = "Section"
        else:
            if hit.div1["type"] and hit.div1["n"]:
                div1_name = hit.div1['type'] + " " + hit.div1["n"]
            else:
                div1_name = hit.div1["head"] or hit.div1['type'] or hit.div1['philo_name'] or hit.div1['philo_type']
    div1_name = div1_name[0].upper() + div1_name[1:]

    ## Remove leading/trailing spaces
    div1_name = div1_name.strip()
    div2_name = hit.div2.head.strip()
    div3_name = hit.div3.head.strip()
    if div3_name == div2_name and hit.div3.philo_id[-1] == 0:
        div3_name = ''
    if div2_name == div1_name and hit.div2.philo_id[-1] == 0:
        div2_name = ''

    if div1_name:
        citation['div1'] = {"href": citation_hrefs['div1'], "label": div1_name}
    else:
        citation['div1'] = {}
    if div2_name:
        citation['div2'] = {"href": citation_hrefs['div2'], "label": div2_name}
    else:
        citation['div2'] = {}
    if div3_name:
        citation['div3'] = {"href": citation_hrefs['div3'], "label": div3_name}
    else:
        citation['div3'] = {}

    ## Paragraph level metadata
    if "para" in citation_hrefs:
        try:
            citation['para'] = {"href": citation_hrefs['para'], "label": hit.who.strip()}
        except KeyError:  ## no who keyword
            citation['para'] = {}

    page_obj = hit.page
    if page_obj['n']:
        page_n = page_obj['n']
        citation['page'] = {"href": citation_hrefs["page"], "label": page_n}
    else:
        citation['page'] = {}
    return citation


def biblio_citation(hit, citation_hrefs):
    """ Returns a representation of a PhiloLogic object suitable for a bibliographic report. """

    citation = {}
    citation['title'] = {'href': citation_hrefs['doc'], 'label': hit.title.strip()}
    if hit.author:
        citation['author'] = {'href': '', 'label': hit.author.strip()}
    else:
        citation['author'] = {}
    if hit.year:
        citation['year'] = {'href': '', 'label': hit.year.strip()}
    else:
        citation["year"] = {}

    ## Div level metadata // Copied from concordance citations
    div1_name = hit.div1.head
    if not div1_name:
        if hit.div1.philo_name == "__philo_virtual":
            div1_name = "Section"
        else:
            if hit.div1["type"] and hit.div1["n"]:
                div1_name = hit.div1['type'] + " " + hit.div1["n"]
            else:
                div1_name = hit.div1["head"] or hit.div1['type'] or hit.div1['philo_name'] or hit.div1['philo_type']
    if div1_name:
        div1_name = div1_name[0].upper() + div1_name[1:]

    ## Remove leading/trailing spaces
    div1_name = div1_name.strip()
    div2_name = hit.div2.head.strip()
    div3_name = hit.div3.head.strip()
    if div3_name == div2_name and hit.div3.philo_id[-1] == 0:
        div3_name = ''
    if div2_name == div1_name and hit.div2.philo_id[-1] == 0:
        div2_name = ''

    if div1_name:
        citation['div1'] = {"href": citation_hrefs['div1'], "label": div1_name}
    else:
        citation['div1'] = {}
    if div2_name:
        citation['div2'] = {"href": citation_hrefs['div2'], "label": div2_name}
    else:
        citation['div2'] = {}
    if div3_name:
        citation['div3'] = {"href": citation_hrefs['div3'], "label": div3_name}
    else:
        citation['div3'] = {}

        ## Paragraph level metadata
    if "para" in citation_hrefs:
        try:
            citation['para'] = {"href": citation_hrefs['para'], "label": hit.who.strip()}
        except KeyError:  ## no who keyword
            citation['para'] = {}

    page_obj = hit.page
    try:
        if page_obj['n']:
            page_n = page_obj['n']
            citation['page'] = {"href": "", "label": page_n}
        else:
            citation['page'] = {}
    except TypeError:
        citation['page'] = {}

    more_metadata = []
    if hit.pub_place:
        citation['pub_place'] = hit.pub_place.strip()
        more_metadata.append(hit.pub_place.strip())
    else:
        citation['pub_place'] = ""
    if hit.publisher:
        citation['publisher'] = hit.publisher.strip()
        more_metadata.append(hit.publisher.strip())
    else:
        citation['publisher'] = ""
    if hit.collection:
        citation['collection'] = hit.collection.strip()
        more_metadata.append(hit.collection.strip())
    else:
        citation['collection'] = ""
    if hit.pub_date:
        citation['pub_date'] = hit.pub_date.strip()
        more_metadata.append(hit.pub_date.strip())
    if hit.genre:
        citation['genre'] = hit.genre.strip()
    else:
        citation['genre'] = ''
    if more_metadata:
        citation['more'] = '%s' % ' || '.join([i for i in more_metadata if i])
    else:
        citation['more'] = ''

    return citation
