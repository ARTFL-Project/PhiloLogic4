#!/usr/bin/env python
import urlparse
import re
import sys
import os
import time
from urllib import quote_plus
from philologic.DB import DB


def make_query_link(query,method=None,methodarg=None,report=None,start=None,end=None,results_per_page=None,collocate=[],**metadata): 
    """ Takes a dictionary of query parameters as produced by parse_cgi, and returns a relative URL representation of such. """
    q_params = [("q",query)]
    if method:
        q_params.append(("method",method))
    if methodarg:
        if method and method =='proxy':
            q_params.append(("arg_proxy", methodarg))
        elif method and method == "phrase":
            q_params.append(('arg_phrase', methodarg))
        else:
            q_params.append(("arg",methodarg))
    metadata = dict([(k, v) for k, v in metadata.items()])
    q_params.extend(metadata.items()[:])
    if report:
        q_params.append(("report",report))
    if start:
        q_params.append(("start" , str(start)))
    if end:
        q_params.append(("end", str(end)))
    if results_per_page:
        q_params.append(("pagenum", str(results_per_page)))
    if collocate:
        q_params.append(('collocate', collocate[0]))
        q_params.append(('direction', collocate[1]))
        q_params.append(('word_num', str(collocate[2])))
        q_params.append(('collocate_num', str(collocate[3])))
    return "./?" + url_encode(q_params)

def url_encode(q_params):
    encoded_str = []
    for k, v in q_params:
        if v:
            encoded_str.append(quote_plus(k, safe='/') + '=' + quote_plus(v, safe='/'))
        else: ## Value is None
            encoded_str.append(quote_plus(k, safe='/') + '=' + '')
    return '&'.join(encoded_str)

def make_object_link(philo_id, hit_bytes):
    """ Takes a valid PhiloLogic object, and returns a relative URL representation of such. """
    href = "./" + "/".join(str(x) for x in philo_id) + byte_query(hit_bytes)
    return href

def make_absolute_object_link(config, id, bytes = []):
    """ Takes a valid PhiloLogic object, and returns an absolute URL representation of such. """
    href = config.db_url + '/dispatcher.py/' + "/".join(str(x) for x in id)
    if bytes:
        href += byte_query(bytes)
    return href
    
def make_absolute_query_link(config, params, script_name="dispatcher.py", **extra_params):
    """ Takes a dictionary of query parameters as produced by WSGIHandler, and returns an absolute URL representation of such. """
    params = dict([i for i in params])
    for k, v in extra_params.iteritems():
        params[k] = v
    query_string = url_encode(params.items())
    href = config.db_url + "/%s?%s" % (script_name, query_string)
    return href
    
def byte_query(hit_bytes):
    """This is used for navigating concordance results and highlighting hits"""
    return '?' + '&'.join(['byte=%d' % int(byte) for byte in hit_bytes])

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

def page_links(config,params,results_len,script_name="dispatcher.py"):
    # pull basic parameters out of the query
    start = params.start
    results_per_page = params.results_per_page

    # first find out what page we are on currently.    
    current_page = start / results_per_page + 1 or 1

    # then how many total pages the query has    
    total_pages = results_len / results_per_page
    remainder = results_len % results_per_page
    if remainder:
        total_pages += 1
    total_pages = total_pages or 1    
    
    # construct the list of page numbers we will output.
    pages = []
    # up to four previous pages
    prev = current_page - 4
    while prev < current_page:
        if prev > 0:
            pages.append(prev)
        prev += 1
    # the current page
    pages.append(current_page)
    # up to five following pages
    next = current_page + 5
    while next > current_page:
        if next < total_pages:
            pages.append(next)
        next -= 1
    # first and last if not already there
    if (pages[0] != 1):
        pages = [1] + pages
    if (pages[-1] != total_pages):
        pages = pages + [total_pages]
    pages.sort()
    
    #now we construct the actual links from the page numbers
    page_links = []
    for page in pages:
        page_start = results_per_page * (page - 1) + 1
        page_end = page_start + results_per_page - 1
        if page_end > results_len:
            page_end = results_len
        link = make_absolute_query_link(config,params,script_name=script_name,start=str(page_start),end=str(page_end), format="json")
        if page == 1 and 2 not in pages:
            page = "First"
        if page == total_pages:
            page = "Last"
            if page == current_page:
                current_page = "Last"
        page_links.append( (page,link) )
    return {"current_page": current_page, "page_links":page_links}
    
def generate_page_links(start, results_per_page, q, results):
    current_page, my_pages, page_num = pager(start, results_per_page, q, results)
    if results.done and page_num != my_pages[-1][0]:
        last_page = find_page_number(len(results), results_per_page)
        last_page_link = page_linker(last_page, results_per_page, q)
    else:
        last_page_link = None
    pages = {"current_page": current_page, "my_pages": my_pages, "page_num": page_num, "last_page_link": last_page_link}
    return pages

def pager(start, results_per_page, q, results):
    results_len = len(results)
    page_num = find_page_number(results_len, results_per_page) or 1 ## We shouldn't have to specify the "or" once we have a no_results template
    current_page = start / results_per_page + 1 or 1

    my_pages = []
    if current_page == 1:
        if page_num >= 9:
            my_pages = [1,2,3,4,5,6,7,8,9]
        else:
            my_pages = range(1,page_num + 1)
    else:
        first = 1 if (current_page - 4) < 1 else current_page - 4
        last = current_page + 5 if current_page + 5 < page_num else page_num
        if last != page_num and (current_page - 4) < 1:
            diff = 1 - (current_page - 4)
            last = last + diff if (last + diff) < page_num else page_num    
        for page in range(first, last):
            my_pages.append(page)
            
    page_links = []
    add_first = False
    if my_pages[0] >= 2:
        my_pages.insert(0, 1)
        add_first = True
    for page in my_pages:     
        page_link = page_linker(page, results_per_page, q)
        if page == 1 and add_first:
            page = 'First'
        page_links.append((page, page_link))
            
    return current_page, page_links, page_num
        
def find_page_number(results_len, results_per_page):
    page_num = results_len / results_per_page
    remainder = results_len % results_per_page
    if remainder:
        page_num += 1
    return page_num

def page_linker(page, results_per_page, q):
    if "collocate" in q:
        collocate = [q['collocate'], q['direction'], q['word_num'], q['collocate_num']]
    else:
        collocate = []
    if page == 1:
        page_start = 1
    else:
        page_start = results_per_page * (page - 1) + 1
    page_end = results_per_page * (page)
    page_link = make_query_link(q["q"],q["method"],q["arg"],q['report'],page_start,page_end,results_per_page,collocate,**q.metadata)    
    return page_link
