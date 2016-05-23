#!/usr/bin/env python

from urllib import quote_plus


def url_encode(q_params):
    encoded_str = []
    for k, v in q_params:
        if v:
            encoded_str.append(quote_plus(k, safe='/') +
                               '=' + quote_plus(v, safe='/'))
        else:  # Value is None
            encoded_str.append(quote_plus(k, safe='/') + '=' + '')
    return '&'.join(encoded_str)


def make_object_link(philo_id, hit_bytes):
    """ Takes a valid PhiloLogic object, and returns a relative URL representation of such. """
    href = "./" + "/".join(str(x) for x in philo_id) + byte_query(hit_bytes)
    return href


def make_absolute_object_link(config, id, bytes=[]):
    """ Takes a valid PhiloLogic object, and returns an absolute URL representation of such. """
    href = config.db_url + '/navigate/' + "/".join(str(x) for x in id)
    if bytes:
        href += byte_query(bytes)
    return href


def make_absolute_query_link(config, params, script_name="query", **extra_params):
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
