"""DB class containing many niceties to retrieve data from SQL"""

import hashlib
import os
import sqlite3
from philologic.Config import Config, DB_LOCALS_DEFAULTS, DB_LOCALS_HEADER

from philologic.runtime import Query

from . import HitList
from . import MetadataQuery
from . import QuerySyntax
from .HitWrapper import HitWrapper, PageWrapper


def hit_to_string(hit, width):
    """Convert Philo hit to a string"""
    if isinstance(hit, sqlite3.Row):
        hit = hit["philo_id"]
    if isinstance(hit, str):
        hit = [int(x) for x in hit.split(" ")]
    if isinstance(hit, int):
        hit = [hit]
    if len(hit) > width:
        hit = hit[:width]
    pad = width - len(hit)
    hit_string = " ".join(str(h) for h in hit)
    hit_string += "".join(" 0" for n in range(pad))
    return hit_string


class DB:
    """Main class to access SQL data"""

    def __init__(self, dbpath, width=7, cached=True):
        """Disabling cache allows to use multiple DB objects in the same script
        without running into collisions"""
        self.path = dbpath
        self.width = width
        self.locals = Config(dbpath + "/db.locals.py", DB_LOCALS_DEFAULTS, DB_LOCALS_HEADER)
        self.cached = cached

    def __getitem__(self, item):
        if self.width != 9:  # verify this isn't a page id
            hit = self.get_id_lowlevel(item)
            hit = [int(x) for x in hit["philo_id"].split(" ")]
            return HitWrapper(hit, self)
        hit = [int(x) for x in hit_to_string(item, 9).split(" ")]
        return PageWrapper(hit, self)

    def __getattr__(self, attr):
        # We need to open DB only when accessed
        # Useful when using a single instance of the DB class accross multiple processors
        if attr == "dbh":
            dbh = sqlite3.connect(self.path + "/toms.db", self.width)
            dbh.text_factory = str
            dbh.row_factory = sqlite3.Row
            setattr(self, "dbh", dbh)
            return self.dbh

    def get_id_lowlevel(self, item):
        """Retrieve text object metadata"""
        hit_s = hit_to_string(item, self.width)
        c = self.dbh.cursor()
        c.execute("SELECT * FROM toms WHERE philo_id=? LIMIT 1;", (hit_s,))
        return c.fetchone()

    def get_word(self, item):
        """Retrieve word from words table"""
        word_s = hit_to_string(item, self.width)
        c = self.dbh.cursor()
        c.execute("SELECT * FROM words WHERE philo_id=? LIMIT 1;", (word_s,))
        return c.fetchone()

    def get_page(self, item):
        """Retrieve page data"""
        page_id_s = " ".join(str(s) for s in item)
        c = self.dbh.cursor()
        c.execute("SELECT * FROM pages WHERE philo_id=? LIMIT 1;", (page_id_s,))
        return c.fetchone()

    def get_line(self, byte_offset, doc_id):
        """Retrieve line data"""
        c = self.dbh.cursor()
        try:
            c.execute(
                "SELECT * FROM lines WHERE doc_id=? and start_byte < ? and end_byte > ? LIMIT 1",
                (doc_id, byte_offset, byte_offset),
            )
            return c.fetchone()
        except sqlite3.OperationalError:
            return ""

    def get_all(self, philo_type="doc", sort_order=["rowid"], raw_results=False):
        """ get all objects of type philo_type """
        hash = hashlib.sha1()
        hash.update(self.path.encode("utf8"))
        hash.update(philo_type.encode("utf8"))
        all_hash = hash.hexdigest()
        all_file = self.path + "/hitlists/" + all_hash + ".hitlist"
        if not os.path.isfile(all_file):
            # write out the corpus file
            if philo_type == "div":
                param_dicts = [{"philo_type": ['"div1"|"div2"|"div3"']}]
            else:
                param_dicts = [{"philo_type": ['"%s"' % philo_type]}]
            return MetadataQuery.metadata_query(self, all_file, param_dicts, sort_order, raw_results=raw_results)
        else:
            return HitList.HitList(all_file, 0, self, sort_order=sort_order, raw=raw_results)

    def query(self, qs="", method="", method_arg="", limit="", sort_order=["rowid"], raw_results=False, **metadata):
        """query the PhiloLogic database"""
        method = method or "proxy"
        if isinstance(method_arg, str):
            try:
                method_arg = int(method_arg)
            except (TypeError, ValueError):
                if method == "cooc" or method == "sentence":
                    method_arg = 6
                else:
                    method_arg = 0

        if isinstance(limit, str):
            try:
                limit = int(limit)
            except (TypeError, ValueError):
                limit = 10000000

        hash = hashlib.sha1()
        hash.update(self.path.encode("utf8"))
        has_metadata = False
        corpus_file = None

        for key, value in metadata.items():
            if isinstance(value, str):
                if value == "":
                    pass
                else:
                    value = [value]
                    metadata[key] = value
            value = [v for v in value if v]
            if value:
                has_metadata = True
                key_value = "%s=%s" % (key, "|".join(value))
                hash.update(key_value.encode("utf8"))

        if has_metadata:
            corpus_hash = hash.hexdigest()
            corpus_file = self.path + "/hitlists/" + corpus_hash + ".hitlist"

            if not os.path.isfile(corpus_file):
                # before we query, we need to figure out what type each parameter belongs to,
                # and sort them into a list of dictionaries, one for each type.
                metadata_dicts = [{} for level in self.locals["metadata_hierarchy"]]
                for k, v in list(metadata.items()):
                    for i, params in enumerate(self.locals["metadata_hierarchy"]):
                        if v and (k in params):
                            metadata_dicts[i][k] = v
                            if k in self.locals["metadata_types"]:
                                this_type = self.locals["metadata_types"][k]
                                if this_type == "div":
                                    metadata_dicts[i]["philo_type"] = ['"div"|"div1"|"div2"|"div3"']
                                else:
                                    metadata_dicts[i]["philo_type"] = ['"%s"' % self.locals["metadata_types"][k]]
                metadata_dicts = [d for d in metadata_dicts if d]
                if "philo_id" in metadata:
                    if metadata_dicts:
                        metadata_dicts[-1]["philo_id"] = metadata["philo_id"]
                    else:
                        metadata_dicts.append({"philo_id": metadata["philo_id"]})
                corpus = MetadataQuery.metadata_query(self, corpus_file, metadata_dicts, sort_order)
            else:
                if sort_order == ["rowid"]:
                    sort_order = None
                corpus = HitList.HitList(corpus_file, 0, self, sort_order=sort_order, raw=raw_results)
                corpus.finish()
            if len(corpus) == 0:
                return corpus
        else:
            corpus = None
        if qs:
            hash.update(qs.encode("utf8"))
            hash.update(method.encode("utf8"))
            hash.update(str(method_arg).encode("utf8"))
            hash.update(str(limit).encode("utf8"))
            search_hash = hash.hexdigest()
            search_file = self.path + "/hitlists/" + search_hash + ".hitlist"
            if sort_order == ["rowid"]:
                sort_order = None
            if not os.path.isfile(search_file):
                return Query.query(
                    self,
                    qs,
                    corpus_file,
                    self.width,
                    method,
                    method_arg,
                    limit,
                    filename=search_file,
                    sort_order=sort_order,
                    raw_results=raw_results,
                )
            parsed = QuerySyntax.parse_query(qs)
            grouped = QuerySyntax.group_terms(parsed)
            split = Query.split_terms(grouped)
            words_per_hit = len(split)
            return HitList.HitList(search_file, words_per_hit, self, sort_order=sort_order, raw=raw_results)
        if corpus:
            return corpus
        return self.get_all(self.locals["default_object_level"], sort_order)
