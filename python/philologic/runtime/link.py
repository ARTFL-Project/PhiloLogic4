#!/usr/bin/env python3
"""Build PhiloLogic links"""

from urllib.parse import quote_plus


def url_encode(q_params):
    """URL encode."""
    encoded_str = []
    for k, v in q_params:
        if v:
            if isinstance(v, list):
                for s in v:
                    encoded_str.append(f'{quote_plus(k, safe="/")}={quote_plus(s, safe="/")}')
            else:
                encoded_str.append(f'{quote_plus(k, safe="/")}={quote_plus(v, safe="/")}')
        else:  # Value is None
            encoded_str.append(f'{quote_plus(k, safe="/")}=')
    return "&".join(encoded_str)


def make_object_link(philo_id, hit_bytes):
    """Takes a valid PhiloLogic object, and returns a relative URL representation of such."""
    href = f'./{"/".join(map(str, philo_id))}{byte_query(hit_bytes)}'
    return href


def make_absolute_object_link(config, philo_id, byte_offsets=None):
    """Takes a valid PhiloLogic object, and returns an absolute URL representation of such."""
    href = f"/navigate/{'/'.join(map(str, philo_id))}"
    if byte_offsets is not None:
        href += byte_query(byte_offsets)
    return href


def make_absolute_query_link(config, params, script_name="/query", **extra_params):
    """Takes a dictionary of query parameters as produced by WSGIHandler,
    and returns an absolute URL representation of such."""
    params = dict([i for i in params])
    for k, v in extra_params.items():
        params[k] = v
    query_string = url_encode(list(params.items()))
    if script_name:
        return f"{script_name}?{query_string}"
    return query_string


def byte_query(hit_bytes):
    """This is used for navigating concordance results and highlighting hits"""
    return f'?{"&".join([f"byte={byte}" for byte in hit_bytes])}'


def make_byte_range_link(config, philo_id, start_byte, end_byte):
    """Return an absolute link with byte range to highlight"""
    href = make_absolute_object_link(config, philo_id.split())
    href += f"?start_byte={start_byte}&end_byte={end_byte}"
    return href


def byte_range_to_link(db, config, request, obj_level="div1"):
    """Find container objects for given byte range and doc id and return links"""
    cursor = db.dbh.cursor()
    cursor.execute("SELECT philo_id FROM toms WHERE filename=?", (request.filename,))
    doc_id = cursor.fetchone()[0].split()[0]
    cursor.execute(
        f"SELECT philo_id FROM toms WHERE philo_type='{obj_level}' AND philo_id like '{doc_id} %' AND cast(start_byte as decimal) <= {request.start_byte} ORDER BY rowid desc"
    )
    philo_id = cursor.fetchone()[0]
    philo_id = philo_id.split()
    while int(philo_id[-1]) == 0:
        philo_id.pop()
    link = make_byte_range_link(config, " ".join(philo_id), request.start_byte, request.end_byte)
    return link
