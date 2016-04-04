#!/usr/bin/env python
"""Parses queries stored in the environ object."""

import Cookie
import hashlib
import urlparse

import parse_query


class WSGIHandler(object):
    """Class which parses the environ object and massages query arguments for PhiloLogic4."""

    def __init__(self, db, environ):
        """Initialize class."""
        self.path_info = environ.get("PATH_INFO", '')
        self.query_string = environ["QUERY_STRING"]
        self.script_filename = environ["SCRIPT_FILENAME"]
        self.authenticated = False
        if "HTTP_COOKIE" in environ:
            # print >> sys.stderr, 'COOKIE', environ['HTTP_COOKIE']
            self.cookies = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
            if "hash" and "timestamp" in self.cookies:
                h = hashlib.md5()
                secret = db.locals.secret
                h.update(environ['REMOTE_ADDR'])
                h.update(self.cookies["timestamp"].value)
                h.update(secret)
                if self.cookies["hash"].value == h.hexdigest():
                    # print >> sys.stderr, "AUTHENTICATED: ", self.cookies["hash"], " vs ", h.hexdigest()
                    self.authenticated = True
        self.cgi = urlparse.parse_qs(self.query_string, keep_blank_values=True)
        self.defaults = {
            "results_per_page": "25",
            "start": "0",
            "end": "0"
        }

        # Check the header for JSON content_type or look for a format=json
        # keyword
        if 'CONTENT_TYPE' in environ:
            self.content_type = environ['CONTENT_TYPE']
        else:
            self.content_type = 'text/HTML'
        # If format is set, it overrides the content_type
        if "format" in self.cgi:
            if self.cgi['format'][0] == "json":
                self.content_type = "application/json"
            else:
                self.content_type = self.cgi['format'][0] or ''

        # Make byte a direct attribute of the class since it is a special case and
        # can contain more than one element
        if "byte" in self.cgi:
            self.byte = self.cgi['byte']

        # Temporary fix for search term arguments before new core merge
        method = self["method"] or "proxy"
        arg = self["arg"]
        if method == "proxy":
            if not arg:
                arg = self["arg_proxy"]
        elif method == "phrase":
            if not arg:
                arg = self["arg_phrase"]
        elif method == "sentence" or method == "cooc":
            arg = "6"
        if not arg:
            arg = 0
        self.arg = arg
        self.cgi['arg'] = [arg]

        self.metadata_fields = db.locals["metadata_fields"]
        self.metadata = {}
        num_empty = 0

        self.start = int(self['start'])
        self.end = int(self['end'])
        self.results_per_page = int(self['results_per_page'])
        if self.start_date:
            self.start_date = int(self['start_date'])
        if self.end_date:
            self.end_date = int(self['end_date'])

        for field in self.metadata_fields:
            if field in self.cgi and self.cgi[field]:
                # Hack to remove hyphens in Frantext
                if field != "date" and isinstance(self.cgi[field][0], str or unicode):
                    if not self.cgi[field][0].startswith('"'):
                        self.cgi[field][0] = self.cgi[field][0].replace('-', ' ')
                # these ifs are to fix the no results you get when you do a
                # metadata query
                if self["q"] != '':
                    self.metadata[field] = self.cgi[field][0]
                elif self.cgi[field][0] != '':
                    self.metadata[field] = self.cgi[field][0]
            # in case of an empty query
            if field not in self.cgi or not self.cgi[field][0]:
                num_empty += 1

        self.metadata['philo_type'] = self['philo_type']

        if num_empty == len(self.metadata_fields):
            self.no_metadata = True
        else:
            self.no_metadata = False

        try:
            self.path_components = [c for c in self.path_info.split("/") if c]
        except:
            self.path_components = []

        self.approximate = False
        if "approximate" in self.cgi:
            if self.cgi["approximate"][0] == "yes":
                self.approximate = True

        if 'q' in self.cgi:
            self.cgi['q'][0] = parse_query(self.cgi['q'][0], self)
            if self.cgi["q"][0] == "":
                self.no_q = True
            else:
                self.no_q = False
        else:
            self.no_q = True

    def __getattr__(self, key):
        """Return query arg as attribute of class."""
        return self[key]

    def __getitem__(self, key):
        """Return query arg as key of class."""
        if key in self.cgi:
            return self.cgi[key][0]
        elif key in self.defaults:
            return self.defaults[key]
        else:
            return ""

    def __iter__(self):
        """Iterate over query args."""
        for key in self.cgi.keys():
            yield (key, self[key])
