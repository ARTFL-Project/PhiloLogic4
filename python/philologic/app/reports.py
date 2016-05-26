#!/usr/bin/env python
"""All reporting functions."""

import os
import re
import timeit
from ast import literal_eval as eval
from collections import defaultdict

import simplejson
from get_text import *
from link import *
from citations import *
from ObjectFormatter import format_strip
from philologic.DB import DB
from philologic.HitList import CombinedHitlist, ObjectWrapper
from philologic import HitWrapper
from philologic.app import adjust_bytes
from philologic.Query import get_expanded_query


def concordance_results(request, config):
    db = DB(config.db_path + '/data/')
    if request.collocation_type:
        first_hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
        second_hits = db.query(request["left"], request["method"], request["arg"], **request.metadata)
        hits = CombinedHitlist(first_hits, second_hits)
    else:
        hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    start, end, n = page_interval(request['results_per_page'], hits, request.start, request.end)

    concordance_object = {
        "description": {"start": start,
                        "end": end,
                        "results_per_page": request.results_per_page},
        "query": dict([i for i in request]),
        "default_object": db.locals['default_object_level']
    }

    results = []
    for hit in hits[start - 1:end]:
        citation_hrefs = citation_links(db, config, hit)
        metadata_fields = {}
        for metadata in db.locals['metadata_fields']:
            metadata_fields[metadata] = hit[metadata]
        citation = concordance_citation(hit, citation_hrefs)
        context = get_concordance_text(db, hit, config.db_path, config.concordance_length)
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


def bibliography_results(request, config):
    db = DB(config.db_path + '/data/')
    if request.no_metadata:
        hits = db.get_all(db.locals['default_object_level'])
    else:
        hits = db.query(**request.metadata)
    start, end, n = page_interval(request.results_per_page, hits, request.start, request.end)
    bibliography_object = {
        "description": {
            "start": start,
            "end": end,
            "n": n,
            "results_per_page": request.results_per_page
        },
        "query": dict([i for i in request]),
        "default_object": db.locals['default_object_level']
    }
    results = []
    result_type = 'doc'
    for hit in hits[start - 1:end]:
        citation_hrefs = citation_links(db, config, hit)
        metadata_fields = {}
        for metadata in db.locals['metadata_fields']:
            metadata_fields[metadata] = hit[metadata]
        result_type = hit.type
        if hit.type == "doc":
            citation = biblio_citation(hit, citation_hrefs)
        else:
            citation = concordance_citation(hit, citation_hrefs)
        results.append({
            'citation': citation,
            'citation_links': citation_hrefs,
            'philo_id': hit.philo_id,
            "metadata_fields": metadata_fields
        })
    bibliography_object["results"] = results
    bibliography_object['results_length'] = len(hits)
    bibliography_object['query_done'] = hits.done
    bibliography_object['result_type'] = result_type
    return bibliography_object, hits


def collocation_results(request, config):
    db = DB(config.db_path + '/data/')
    if request["collocate_distance"]:
        hits = db.query(request["q"], "proxy", int(request['collocate_distance']), **request.metadata)
    else:
        hits = db.query(request["q"], "cooc", request["arg"], **request.metadata)
    hits.finish()
    collocation_object = {"query": dict([i for i in request])}

    length = config['concordance_length']
    try:
        collocate_distance = int(request['collocate_distance'])
    except ValueError:  # Getting an empty string since the keyword is not specificed in the URL
        collocate_distance = None

    if request.colloc_filter_choice == "nofilter":
        filter_list = []
    else:
        filter_list = build_filter_list(request, config)
    collocation_object['filter_list'] = filter_list
    filter_list = set(filter_list)

    # Build list of search terms to filter out
    query_words = []
    for group in get_expanded_query(hits):
        for word in group:
            word = word.replace('"', '')
            query_words.append(word)
    query_words = set(query_words)
    filter_list = filter_list.union(query_words)

    db = DB(config.db_path + '/data/')
    if request["collocate_distance"]:
        hits = db.query(request["q"], "proxy", int(request['collocate_distance']), **request.metadata)
    else:
        hits = db.query(request["q"], "cooc", request["arg"], **request.metadata)
    hits.finish()

    stored_sentence_id = None
    stored_sentence_counts = defaultdict(int)
    sentence_hit_count = 1
    hits_done = request.start or 0
    max_time = request.max_time or 10
    all_collocates = defaultdict(lambda: {'count': 0})
    cursor = db.dbh.cursor()
    start_time = timeit.default_timer()
    try:
        for hit in hits[hits_done:]:
            word_id = ' '.join([str(i) for i in hit.philo_id])
            query = """select philo_name, parent, rowid from words where philo_id='%s'""" % word_id
            cursor.execute(query)
            result = cursor.fetchone()
            parent = result['parent']
            rowid = int(result['rowid'])
            if parent != stored_sentence_id:
                sentence_hit_count = 1
                stored_sentence_id = parent
                stored_sentence_counts = defaultdict(int)
                if collocate_distance:
                    begin_rowid = rowid - collocate_distance
                    if begin_rowid < 0:
                        begin_rowid = 0
                    end_rowid = rowid + collocate_distance
                    row_query = """select philo_name from words where parent='%s' and rowid between %d and %d""" % (
                        parent, begin_rowid, end_rowid)
                else:
                    row_query = """select philo_name from words where parent='%s'""" % (parent, )
                cursor.execute(row_query)
                for i in cursor.fetchall():
                    stored_sentence_counts[i['philo_name']] += 1
            else:
                sentence_hit_count += 1
            for word in stored_sentence_counts:
                if word in filter_list or stored_sentence_counts[word] < sentence_hit_count:
                    continue
                all_collocates[word]['count'] += 1
            hits_done += 1
            elapsed = timeit.default_timer() - start_time
            # avoid timeouts by splitting the query if more than request.max_time (in
            # seconds) has been spent in the loop
            if elapsed > int(max_time):
                break
    except IndexError:
        collocation['hits_done'] = len(hits)

    collocation_object['collocates'] = all_collocates
    collocation_object["results_length"] = len(hits)
    if hits_done < collocation_object["results_length"]:
        collocation_object['more_results'] = True
        collocation_object['hits_done'] = hits_done
    else:
        collocation_object['more_results'] = False
        collocation_object['hits_done'] = collocation_object["results_length"]

    return collocation_object


def frequency_results(request, config, sorted=False):
    """reads through a hitlist. looks up request.frequency_field in each hit, and builds up a list of
       unique values and their frequencies."""
    db = DB(config.db_path + '/data/')
    if request.q == '' and request.no_q:
        if request.no_metadata:
            hits = db.get_all(db.locals['default_object_level'])
        else:
            hits = db.query(**request.metadata)
    else:
        hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)

    if sorted:
        hits.finish()

    field_list = eval(simplejson.loads(request.frequency_field))

    counts = defaultdict(int)
    frequency_object = {}
    start_time = timeit.default_timer()
    last_hit_done = request.start

    try:
        for hit in hits[request.start:]:
            key = tuple((field, hit[field]) for field in field_list)
            counts[key] += 1

            # avoid timeouts by splitting the query if more than request.max_time (in seconds) has been spent in the loop
            elapsed = timeit.default_timer() - start_time
            last_hit_done += 1
            if elapsed > 5:
                break

        table = {}
        for key, count in counts.iteritems():
            # for each item in the table, we modify the query params to
            # generate a link url.
            # Make a distinct copy for each key in case we modify it below
            metadata = dict(request.metadata)

            # Build a label starting with the first value as the main value
            first_metatada_key, first_metadata_value = key[0] or "NULL"
            label = first_metadata_value
            metadata[first_metatada_key] = first_metadata_value.encode('utf-8', 'ignore')
            append_to_label = []
            for metadata_key, metadata_value in key[1:]:
                if not metadata_value:
                    # replace NULL with '[None]', 'N.A.', 'Untitled', etc.
                    metadata[metadata_key] = "NULL"
                else:
                    # we want to run exact queries on defined values.
                    metadata[metadata_key] = metadata_value.encode('utf-8', 'ignore')
                    append_to_label.append(metadata_value)
            # Add parentheses to other value, as they are secondary
            if append_to_label:
                label = label + ' (' + ', '.join(append_to_label) + ')'

            # Quote metadata to force exact matches on metadata
            for m in metadata:
                if m not in request.metadata:  # skip metadata already in original query: this could be a glob search
                    if metadata[m] and m != "date" and metadata[m] != "NULL":
                        if not metadata[m].startswith('"'):
                            metadata[m] = '"%s"' % metadata[m]
            # Now build the url from request.
            url = make_absolute_query_link(config,
                                           request,
                                           frequency_field="",
                                           start="0",
                                           end="0",
                                           report=request.report,
                                           script='',
                                           **metadata)
            table[label] = {'count': count, 'url': url, 'metadata': metadata}
        frequency_object['results'] = table
        frequency_object["hits_done"] = last_hit_done
        if last_hit_done == len(hits):
            frequency_object['more_results'] = False
        else:
            frequency_object['more_results'] = True
    except IndexError:
        frequency_object['results'] = {}
        frequency_object['more_results'] = False
    frequency_object['results_length'] = len(hits)
    frequency_object['query'] = dict([i for i in request])

    if sorted:
        frequency_object["results"] = sorted(frequency_object['results'].iteritems(), key=lambda x: x[1]['count'], reverse=True)

    return frequency_object


def kwic_results(request, config):
    """ The link_to_hit keyword defines the text object to which the metadata link leads to"""
    db = DB(config.db_path + '/data/')
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    start, end, n = page_interval(request.results_per_page, hits, request.start, request.end)
    kwic_object = {
        "description": {"start": start,
                        "end": end,
                        "results_per_page": request.results_per_page},
        "query": dict([i for i in request])
    }
    kwic_results = []

    for hit in hits[start - 1:end]:
        kwic_result = kwic_hit_object(hit, config, db)
        kwic_results.append(kwic_result)

    kwic_object['results'] = kwic_results
    kwic_object['results_length'] = len(hits)
    kwic_object["query_done"] = hits.done

    return kwic_object


def generate_text_object(request, config, note=False):
    db = DB(config.db_path + '/data/')
    try:
        obj = db[request.philo_id]
    except ValueError:
        philo_id = ' '.join(request.path_components)
        obj = db[philo_id]
    philo_id = obj.philo_id
    while obj['philo_name'] == '__philo_virtual' and obj["philo_type"] != "div1":
        philo_id.pop()
        obj = db[philo_id]
    philo_id = list(obj.philo_id)
    while philo_id[-1] == 0:
        philo_id.pop()
    text_object = {"query": dict([i for i in request]), "philo_id": ' '.join([str(i) for i in philo_id])}
    text_object['prev'] = neighboring_object_id(db, obj.prev)
    text_object['next'] = neighboring_object_id(db, obj.next)
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        if db.locals['metadata_types'][metadata] == "doc":
            metadata_fields[metadata] = obj[metadata]
    text_object['metadata_fields'] = metadata_fields
    citation_hrefs = citation_links(db, config, obj)
    citation = biblio_citation(obj, citation_hrefs)
    text_object['citation'] = citation
    text, imgs = get_text_obj(obj, config, request, db.locals['word_regex'], note=note)
    text_object['text'] = text
    text_object['imgs'] = imgs
    return text_object


def generate_toc_object(request, config):
    """This function fetches all philo_ids for div elements within a doc"""
    db = DB(config.db_path + '/data/')
    conn = db.dbh
    c = conn.cursor()
    try:
        obj = db[request.philo_id]
    except ValueError:
        philo_id = ' '.join(request.path_components[:-1])
        obj = db[philo_id]
    doc_id = int(obj.philo_id[0])
    next_doc_id = doc_id + 1
    # find the starting rowid for this doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % doc_id)
    start_rowid = c.fetchone()[0]
    # find the starting rowid for the next doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % next_doc_id)
    try:
        end_rowid = c.fetchone()[0]
    except TypeError:  # if this is the last doc, just get the last rowid in the table.
        c.execute('select max(rowid) from toms;')
        end_rowid = c.fetchone()[0]

    # use start_rowid and end_rowid to fetch every div in the document.
    philo_slices = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}
    text_hierarchy = []
    c.execute("select * from toms where rowid >= ? and rowid <=? and philo_type>='div' and philo_type<='div3'",
              (start_rowid, end_rowid))
    for row in c.fetchall():
        philo_id = [int(n) for n in row["philo_id"].split(" ")]
        text = HitWrapper.ObjectWrapper(philo_id, db, row=row)
        if text['philo_name'] == '__philo_virtual' and text["philo_type"] != "div1":
            continue
        elif text['word_count'] == 0:
            continue
        else:
            philo_id = text['philo_id']
            philo_type = text['philo_type']
            display_name = ""
            if text['philo_name'] == "front":
                display_name = "Front Matter"
            elif text['philo_name'] == "note":
                continue
            else:
                display_name = text['head']
                if display_name:
                    display_name = display_name.strip()
                if not display_name:
                    if text["type"] and text["n"]:
                        display_name = text['type'] + " " + text["n"]
                    else:
                        display_name = text["head"] or text['type'] or text['philo_name'] or text['philo_type']
                        if display_name == "__philo_virtual":
                            display_name = text['philo_type']
            display_name = display_name[0].upper() + display_name[1:]
            link = make_absolute_object_link(config, philo_id.split()[:philo_slices[philo_type]])
            philo_id = ' '.join(philo_id.split()[:philo_slices[philo_type]])
            toc_element = {"philo_id": philo_id, "philo_type": philo_type, "label": display_name, "href": link}
            text_hierarchy.append(toc_element)
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        if db.locals['metadata_types'][metadata] == "doc":
            metadata_fields[metadata] = obj[metadata]
    citation_hrefs = citation_links(db, config, obj)
    citation = biblio_citation(obj, citation_hrefs)
    toc_object = {"query": dict([i for i in request]),
                  "philo_id": obj.philo_id,
                  "toc": text_hierarchy,
                  "metadata_fields": metadata_fields,
                  "citation": citation}
    return toc_object


def generate_time_series(request, config):
    db = DB(config.db_path + '/data/')
    time_series_object = {'query': dict([i for i in request]), 'query_done': False}

    start_date, end_date = get_start_end_date(db, start_date=None, end_date=None)

    # Generate date ranges
    interval = int(request.year_interval)
    date_ranges = []
    for i in xrange(start_date, end_date, interval):
        start = i
        end = i + interval - 1
        if end > end_date:
            end = end_date
        date_range = "%d-%d" % (start, end)
        date_ranges.append((start, date_range))

    absolute_count = defaultdict(int)
    date_counts = {}
    total_hits = 0
    last_date_done = start_date
    start_time = timeit.default_timer()
    max_time = request.max_time or 10
    for start_range, date_range in date_ranges:
        request.metadata['date'] = date_range
        hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
        hits.finish()
        url = make_absolute_query_link(config, request, report="concordance", date=date_range, start="0", end="0")
        absolute_count[start_range] = {"label": start_range, "count": len(hits), "url": url}

        # Get date total count
        if interval != '1':
            dates = [start_range]
            dates.append(start_range + (int(request['year_interval']) - 1))
            query = 'select sum(word_count) from toms where date between "%d" and "%d"' % tuple(dates)
        else:
            query = "select sum(word_count) from toms where date='%s'" % start_range
        c = db.dbh.cursor()
        c.execute(query)
        date_counts[start_range] = c.fetchone()[0] or 0
        total_hits += len(hits)
        elapsed = timeit.default_timer() - start_time
        # avoid timeouts by splitting the query if more than request.max_time (in seconds) has been spent in the loop
        if elapsed > int(max_time):
            last_date_done = start_range
            break
        last_date_done = start_range

    time_series_object['results_length'] = total_hits
    if (last_date_done + int(request.year_interval)) >= end_date:
        time_series_object['more_results'] = False
    else:
        time_series_object['more_results'] = True
        time_series_object['new_start_date'] = last_date_done + int(request.year_interval)
    time_series_object['results'] = {'absolute_count': absolute_count, 'date_count': date_counts}

    return time_series_object


def filter_words_by_property(request, config):
    db = DB(config.db_path + '/data/')
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
        ## get my chunk of text ##
        hit_val = get_word_attrib(hit, word_property, db)

        if hit_val == word_property_value:
            position += 1
            if position < start:
                continue
            new_hitlist.append(hit)
            citation_hrefs = citation_links(db, config, hit)
            metadata_fields = {}
            for metadata in db.locals['metadata_fields']:
                metadata_fields[metadata] = hit[metadata]
            citation = concordance_citation(hit, citation_hrefs)
            context = fetch_concordance(db, hit, config.db_path, config.concordance_length)
            result_obj = {
                "philo_id": hit.philo_id,
                "citation": citation,
                "citation_links": citation_hrefs,
                "context": context,
                "metadata_fields": metadata_fields,
                "bytes": hit.bytes,
                "collocate_count": 1
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
    concordance_object['results'] = results
    concordance_object["query_done"] = hits.done
    concordance_object['results_length'] = word_property_total
    concordance_object["description"] = {
        "start": start,
        "end": end,
        "results_per_page": request.results_per_page,
        "more_pages": more_pages
    }
    return concordance_object


def generate_word_frequency(request, config):
    """reads through a hitlist. looks up request["field"] in each hit, and builds up a list of
       unique values and their frequencies."""
    db = DB(config.db_path + '/data/')
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    field = request["field"]
    counts = {}
    frequency_object = {}
    more_results = True
    start_time = timeit.default_timer()
    last_hit_done = request.start
    try:
        for n in hits[request.start:]:
            key = get_word_attrib(n, field, db)
            if not key:
                # NULL is a magic value for queries, don't change it
                # recklessly.
                key = "NULL"
            if key not in counts:
                counts[key] = 0
            counts[key] += 1
            elapsed = timeit.default_timer() - start_time
            last_hit_done += 1
            if elapsed > 5:
                break

        table = {}
        for k, v in counts.iteritems():
            url = make_absolute_query_link(config,
                                           request,
                                           start="0",
                                           end="0",
                                           report="word_property_filter",
                                           word_property=field,
                                           word_property_value=k)
            table[k] = {'count': v, 'url': url}

        frequency_object['results'] = table
        frequency_object["hits_done"] = last_hit_done
        if last_hit_done == len(hits):
            frequency_object['more_results'] = False
        else:
            frequency_object['more_results'] = True

    except IndexError:
        frequency_object['results'] = {}
        frequency_object['more_results'] = False

    frequency_object['results_length'] = len(hits)
    frequency_object['query'] = dict([i for i in request])

    return frequency_object


# Shared function
def page_interval(num, results, start, end):
    start = int(start)
    end = int(end)
    num = int(num)
    if start <= 0:
        start = 1
    if end <= 0:
        end = start + (num - 1)
    results_len = len(results)
    if end > results_len and results.done:
        end = results_len
    n = start - 1
    return start, end, n


def neighboring_object_id(db, philo_id):
    if not philo_id:
        return ''
    philo_id = philo_id.split()[:7]
    while philo_id[-1] == '0':
        philo_id.pop()
    philo_id = str(" ".join(philo_id))
    obj = db[philo_id]
    if obj['philo_name'] == '__philo_virtual' and obj["philo_type"] != "div1":
        # Remove the last number (1) in the philo_id and point to one object level lower
        philo_id = ' '.join(philo_id.split()[:-1])
    return philo_id


def get_word_attrib(n, field, db):
    words = n.words
    key = field
    if key == "token":
        key = "philo_name"
    if key == "morph":
        key = "pos"
    val = ""
    for word in words:
        word_obj = word
        if val:
            val += "_"
        if word_obj[key]:
            val += word_obj[key]
        else:
            val += "NULL"

    if isinstance(val, unicode):
        return val.encode("utf-8")
    return val


def build_filter_list(request, config):
    """set up filtering with stopwords or most frequent terms."""
    if config.stopwords and request.colloc_filter_choice == "stopwords":
        if os.path.isabs(config.stopwords):
            filter_file = open(config.stopwords)
        else:
            filter_file = os.path.join(config.db_path, config.stopwords)
        filter_num = float("inf")
    else:
        filter_file = open(config.db_path + '/data/frequencies/word_frequencies')
        if request.filter_frequency:
            filter_num = int(request.filter_frequency)
        else:
            filter_num = 100  # default value in case it's not defined
    filter_list = [request['q']]
    for line_count, line in enumerate(filter_file):
        if line_count == filter_num:
            break
        try:
            word = line.split()[0]
        except IndexError:
            continue
        filter_list.append(word)
    return filter_list


def kwic_hit_object(hit, config, db):
    """Build an individual kwic concordance"""
    # Get all metadata
    metadata_fields = {}
    for metadata in db.locals['metadata_fields']:
        metadata_fields[metadata] = hit[metadata].strip()

    ## Get all links and citations
    citation_hrefs = citation_links(db, config, hit)
    citation = concordance_citation(hit, citation_hrefs)

    ## Determine length of text needed
    byte_distance = hit.bytes[-1] - hit.bytes[0]
    length = config.concordance_length + byte_distance + config.concordance_length

    ## Get concordance and align it
    bytes, byte_start = adjust_bytes(hit.bytes, config.concordance_length)
    conc_text = get_text(hit, byte_start, length, config.db_path)
    conc_text = format_strip(conc_text, bytes)
    conc_text = conc_text.replace('\n', ' ')
    conc_text = conc_text.replace('\r', '')
    conc_text = conc_text.replace('\t', ' ')
    try:
        start_hit = conc_text.index('<span class="highlight">')
        start_output = '<span class="kwic-before"><span class="inner-before">' + conc_text[:
                                                                                           start_hit] + '</span></span>'
        end_hit = conc_text.rindex('</span>') + 7
        end_output = '<span class="kwic-after">' + conc_text[end_hit:] + '</span>'
        conc_text = '<span class="kwic-text">' + start_output + '&nbsp;<span class="kwic-highlight">' + conc_text[
            start_hit:end_hit] + "</span>&nbsp;" + end_output + '</span>'
    except ValueError:
        pass

    highlighted_text = conc_text[start_hit:end_hit]

    kwic_result = {
        "philo_id": hit.philo_id,
        "context": conc_text,
        "highlighted_text": highlighted_text,
        "metadata_fields": metadata_fields,
        "citation_links": citation_hrefs,
        "citation": citation,
        "bytes": hit.bytes
    }

    return kwic_result


def get_start_end_date(db, start_date=None, end_date=None):
    date_finder = re.compile(r'^.*?(\d{1,}).*')
    c = db.dbh.cursor()
    c.execute('select date from toms where date is not null')
    dates = []
    for i in c.fetchall():
        try:
            dates.append(int(i[0]))
        except:
            date_match = date_finder.search(i[0])
            if date_match:
                dates.append(int(date_match.groups()[0]))
            else:
                pass
    min_date = min(dates)
    start_date = start_date or min_date
    if start_date < min_date:
        start_date = min_date
    max_date = max(dates)
    end_date = end_date or max_date
    if end_date > max_date:
        end_date = max_date
    return start_date, end_date
