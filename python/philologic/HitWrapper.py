#!/usr/bin/python

from __future__ import absolute_import
from __future__ import print_function
import sys
from six.moves import zip

obj_dict = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4, 'para': 5, 'sent': 6, 'word': 7}


def _safe_lookup(row, field, encoding="utf-8"):
    metadata = ""
    try:
        metadata = row[field]
    except:
        pass
    if metadata is None:
        return u""
    metadata_string = ""
    try:
        metadata_string = metadata.decode(encoding, "ignore")
    except AttributeError:
        metadata_string = str(metadata).decode(encoding, "ignore")
    return metadata_string


shared_cache = {}


class HitWrapper(object):
    def __init__(self, hit, db, obj_type=False, encoding=None):
        self.db = db
        self.hit = hit
        if obj_type:
            self.object_type = obj_type
        else:
            try:
                length = len(hit[:hit.index(0)])
            except ValueError:
                length = len(hit)
            if length >= 7:
                length = 7
            self.object_type = [k for k in obj_dict if obj_dict[k] == length][0]
        self.row = None
        self.bytes = []
        self.words = []
        if len(list(hit)) == 7:
            self.philo_id = hit
            self.words.append(WordWrapper(hit, db, self.start_byte))
            page_i = self["page"]
        else:
            self.philo_id = hit[:6] + (self.hit[7], )
            parent_id = self.hit[:6]
            remaining = list(self.hit[7:])
            while remaining:
                self.words += [parent_id + (remaining.pop(0), )]
                if remaining:
                    self.bytes.append(remaining.pop(0))
            self.bytes.sort()
            self.words.sort(key=lambda x: x[-1])  # assumes words in same sent, as does search4
            self.words = [WordWrapper(word, db, byte) for word, byte in zip(self.words, self.bytes)]

            page_i = self.hit[6]
        page_id = [self.hit[0], 0, 0, 0, 0, 0, 0, 0, page_i]
        self.page = PageWrapper(page_id, db)
        self.ancestors = {}
        for t, n in obj_dict.items():
            if t == "word":
                self.ancestors["word"] = self.words[0]
            else:
                self.ancestors[t] = ObjectWrapper(self.hit, self.db, t)
        try:
            self.line = LineWrapper(self.philo_id, self.bytes[0], db)
        except IndexError:
            self.line = ""

    def __getitem__(self, key):
        if key in obj_dict:
            return self.ancestors[key]
        else:
            if key in self.db.locals["metadata_fields"]:
                f_type = self.db.locals["metadata_types"][key]
                if f_type == "div":
                    for div_type in ("div3", "div2", "div1"):
                        val = self.ancestors[div_type][key]
                        if val:
                            break
                    return val
                elif f_type == "line":
                    try:
                        return LineWrapper(self.philo_id, self.bytes[0], self.db)["n"]
                    except IndexError:
                        # Not a word hit
                        return ""
                else:
                    try:
                        return self.ancestors[f_type][key]
                    except KeyError:
                        return ""
            else:
                if self.row is None:
                    self.row = self.db.get_id_lowlevel(self.philo_id)
                return _safe_lookup(self.row, key, self.db.encoding)

    def __getattr__(self, name):
        return self[name]


class ObjectWrapper(object):
    def __init__(self, hit, db, obj_type=False, row=None):
        self.db = db
        self.hit = hit
        if obj_type:
            self.philo_id = hit[:obj_dict[obj_type]]
            self.object_type = obj_type
        else:
            self.philo_id = hit
            try:
                length = len(hit[:hit.index(0)])
            except ValueError:
                length = len(hit)
            self.object_type = [k for k in obj_dict if obj_dict[k] == length][0]
        self.bytes = []
        self.row = row
        self.words = []
        page_i = self["page"]
        page_id = [self.hit[0], 0, 0, 0, 0, 0, 0, 0, page_i]
        self.page = PageWrapper(page_id, db)

    def __getitem__(self, key):
        if key in obj_dict:
            return ObjectWrapper(self.hit, self.db, key)
        else:
            if self.object_type in shared_cache:
                philo_id, row = shared_cache[self.object_type]
                if philo_id == self.philo_id:
                    self.row = row
            if self.row is None:
                self.row = self.db.get_id_lowlevel(self.philo_id)
                shared_cache[self.object_type] = (self.philo_id, self.row)
            return _safe_lookup(self.row, key, self.db.encoding)

    def __getattr__(self, name):
        return self[name]


class PageWrapper(object):
    def __init__(self, id, db):
        self.db = db
        self.philo_id = id
        self.object_type = "page"
        self.row = None
        self.bytes = []

    def __getitem__(self, key):
        if self.row is None:
            self.row = self.db.get_page(self.philo_id)
        return _safe_lookup(self.row, key, self.db.encoding)

    def __getattr__(self, name):
        if name in obj_dict:
            return ObjectWrapper(self.philo_id, self.db)
        elif name == "page":
            return self
        else:
            return self[name]


class LineWrapper(object):
    def __init__(self, philo_id, byte_offset, db):
        self.db = db
        self.philo_id = philo_id
        self.doc_id = philo_id[0]
        self.object_type = "line"
        self.hit_offset = byte_offset
        self.row = None
        self.bytes = []

    def __getitem__(self, key):
        if self.row is None:
            self.row = self.db.get_line(self.hit_offset, self.doc_id)
        return _safe_lookup(self.row, key, self.db.encoding)

    def __getattr__(self, name):
        if name in obj_dict:
            return ObjectWrapper(self.philo_id, self.db)
        elif name == "line":
            return self
        else:
            return self[name]


class WordWrapper(object):
    def __init__(self, id, db, byte):
        self.db = db
        self.philo_id = id
        self.object_type = "word"
        self.row = None
        self.byte = byte

    def __getitem__(self, key):
        if self.row is None:
            self.row = self.db.get_word(self.philo_id)
            if self.row is None:
                print("WORD LOOKUP ERROR for ", repr(self.philo_id), file=sys.stderr)
        return _safe_lookup(self.row, key, self.db.encoding)

    def __getattr__(self, name):
        return self[name]
