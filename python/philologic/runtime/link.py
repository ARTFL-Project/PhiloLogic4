#!/usr/bin/env python

from __future__ import absolute_import

import imp
import os
from urllib import quote_plus

import six
from philologic.Config import MakeWebConfig
from philologic.DB import DB


def url_encode(q_params):
    """URL encode."""
    encoded_str = []
    for k, v in q_params:
        if v:
            if isinstance(v, list):
                for s in v:
                    encoded_str.append(quote_plus(k, safe='/') + '=' + quote_plus(s, safe='/'))
            else:
                try:
                    encoded_str.append(quote_plus(k, safe='/') + '=' + quote_plus(v, safe='/'))
                except KeyError:
                    encoded_str.append(quote_plus(k, safe='/') + '=' + quote_plus(v.encode('utf8'), safe='/'))
        else:  # Value is None
            encoded_str.append(quote_plus(k, safe='/') + '=' + '')
    return '&'.join(encoded_str)


def make_object_link(philo_id, hit_bytes):
    """ Takes a valid PhiloLogic object, and returns a relative URL representation of such. """
    href = "./" + "/".join(str(x) for x in philo_id) + byte_query(hit_bytes)
    return href


def make_absolute_object_link(config, philo_id, bytes=None):
    """ Takes a valid PhiloLogic object, and returns an absolute URL representation of such. """
    href = 'navigate/' + "/".join(str(x) for x in philo_id)
    if bytes is not None:
        href += byte_query(bytes)
    return href


def make_absolute_query_link(config, params, script_name="query", **extra_params):
    """ Takes a dictionary of query parameters as produced by WSGIHandler,
    and returns an absolute URL representation of such. """
    params = dict([i for i in params])
    for k, v in six.iteritems(extra_params):
        params[k] = v
    query_string = url_encode(list(params.items()))
    href = "%s?%s" % (script_name, query_string)
    return href


def byte_query(hit_bytes):
    """This is used for navigating concordance results and highlighting hits"""
    return '?' + '&'.join(['byte=%d' % int(byte) for byte in hit_bytes])


def make_byte_range_link(config, philo_id, start_byte, end_byte):
    """Return an absolute link with byte range to highlight"""
    href = make_absolute_object_link(config, philo_id.split())
    href += "?start_byte={}&end_byte={}".format(start_byte, end_byte)
    return href


def byte_range_to_link(db_path, doc_id, start_byte, end_byte, obj_level='div1', global_config_path=None):
    """Find container objects for given byte range and doc id and return links"""
    db = DB(db_path+'/data')
    config = MakeWebConfig(db_path+'/data/web_config.cfg')
    if global_config_path is None:
        global_config_path = os.getenv("PHILOLOGIC_CONFIG", "/etc/philologic/philologic5.cfg")
    global_config = imp.load_source("", global_config_path)
    url_root = os.path.join(global_config.url_root, [i for i in db_path.split("/") if i][-1])
    cursor = db.dbh.cursor()
    doc_id = "{} %".format(doc_id)
    cursor.execute("SELECT rowid, philo_id FROM toms WHERE philo_type='{}' \
                    AND philo_id LIKE '{}' AND start_byte <= {} ORDER BY rowid desc".format(obj_level, doc_id, start_byte))
    rowid, first_id = cursor.fetchone()
    parent_links = [os.path.join(url_root, make_byte_range_link(config, first_id, start_byte, end_byte))]
    cursor.execute("SELECT philo_id, start_byte FROM toms WHERE philo_type='{}' \
                    AND philo_id LIKE '{}' AND rowid > {}".format(obj_level, doc_id, rowid))
    for obj_id, obj_id_start in cursor:
        if obj_id_start > end_byte:
            break
        parent_links.append(os.path.join(url_root, make_byte_range_link(config, obj_id, start_byte, end_byte)))
    return parent_links
