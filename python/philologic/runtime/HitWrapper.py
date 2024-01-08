#!/usr/bin/python3
"""All different types of hit objects"""

TEXT_OBJECT_LEVELS = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5, "sent": 6, "word": 7}
SHARED_CACHE = {}


def _safe_lookup(row, field):
    metadata = ""
    try:
        metadata = row[field]
    except:
        pass
    if metadata is None:
        return ""
    return metadata


class HitWrapper:
    """Class representing an individual hit with all its ancestors"""

    __slots__ = ["db", "hit", "object_type", "row", "bytes", "words", "philo_id", "page", "line", "ancestors"]

    def __init__(self, hit, db, obj_type=False, method="proxy"):
        self.db = db
        self.hit = hit
        if obj_type:
            self.object_type = obj_type
        else:
            try:
                length = len(hit[: hit.index(0)])
            except ValueError:
                length = len(hit)
            if length >= 7:
                length = 7
            self.object_type = [k for k in TEXT_OBJECT_LEVELS if TEXT_OBJECT_LEVELS[k] == length][0]
        self.row = None
        self.bytes = []
        self.words = []
        if len(list(hit)) == 7:
            self.philo_id = hit
            self.words.append(WordWrapper(hit, db, self.start_byte))
            page_i = self["page"]
        else:
            self.philo_id = hit[:7]
            parent_id = self.hit[:6]
            remaining = list(self.hit[7:])
            while remaining:
                self.words += [parent_id + (remaining.pop(0),)]
                if remaining:
                    self.bytes.append(remaining.pop(0))
            self.bytes.sort()
            self.words.sort(key=lambda x: x[-1])  # assumes words in same sent, as does search4
            self.words = [WordWrapper(word, db, byte) for word, byte in zip(self.words, self.bytes)]
            page_i = self.hit[6]
        page_id = [self.hit[0], 0, 0, 0, 0, 0, 0, 0, page_i]
        self.page = PageWrapper(page_id, db)
        self.ancestors = {}
        for object_type in TEXT_OBJECT_LEVELS:
            if object_type == "word":
                self.ancestors["word"] = self.words[0]
            else:
                self.ancestors[object_type] = ObjectWrapper(self.hit, self.db, object_type)
        try:
            self.line = LineWrapper(self.philo_id, self.bytes[0], db)
        except IndexError:
            self.line = ""

    def __getitem__(self, key):
        if key in TEXT_OBJECT_LEVELS:
            return self.ancestors[key]
        else:
            if key in self.db.locals["metadata_fields"]:
                try:
                    f_type = self.db.locals["metadata_types"][key]
                except KeyError:
                    return ""
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
                return _safe_lookup(self.row, key)

    def __getattr__(self, name):
        return self[name]


class ObjectWrapper:
    """Class representing doc, div1, div2, div3, para, sent objects"""

    __slots__ = ["db", "hit", "object_type", "row", "bytes", "words", "philo_id", "page"]

    def __init__(self, hit, db, obj_type=False, row=None):
        self.db = db
        self.hit = hit
        if obj_type:
            self.philo_id = hit[: TEXT_OBJECT_LEVELS[obj_type]]
            self.object_type = obj_type
        else:
            self.philo_id = hit
            try:
                length = len(hit[: hit.index(0)])
            except ValueError:
                length = len(hit)
            self.object_type = [k for k in TEXT_OBJECT_LEVELS if TEXT_OBJECT_LEVELS[k] == length][0]
        self.bytes = []
        self.row = row
        self.words = []
        page_i = self["page"]
        page_id = [self.hit[0], 0, 0, 0, 0, 0, 0, 0, page_i]
        self.page = PageWrapper(page_id, db)

    def __getitem__(self, key):
        if key in TEXT_OBJECT_LEVELS:
            return ObjectWrapper(self.hit, self.db, key)
        else:
            if self.object_type in SHARED_CACHE:
                philo_id, row = SHARED_CACHE[self.object_type]
                if philo_id == self.philo_id:
                    self.row = row
            if self.row is None:
                self.row = self.db.get_id_lowlevel(self.philo_id)
                if self.db.cached:
                    SHARED_CACHE[self.object_type] = (self.philo_id, self.row)
            return _safe_lookup(self.row, key)

    def __getattr__(self, name):
        return self[name]


class PageWrapper:
    """Class representing page objects"""

    __slots__ = ["db", "philo_id", "object_type", "row", "bytes"]

    def __init__(self, id, db):
        self.db = db
        self.philo_id = id
        self.object_type = "page"
        self.row = None
        self.bytes = []

    def __getitem__(self, key):
        if self.row is None:
            self.row = self.db.get_page(self.philo_id)
        return _safe_lookup(self.row, key)

    def __getattr__(self, name):
        if name in TEXT_OBJECT_LEVELS:
            return ObjectWrapper(self.philo_id, self.db)
        elif name == "page":
            return self
        else:
            return self[name]


class LineWrapper:
    """Class representing line objects"""

    __slots__ = ["db", "philo_id", "object_type", "row", "bytes", "doc_id", "hit_offset"]

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
        return _safe_lookup(self.row, key)

    def __getattr__(self, name):
        if name in TEXT_OBJECT_LEVELS:
            return ObjectWrapper(self.philo_id, self.db)
        elif name == "line":
            return self
        else:
            return self[name]


class WordWrapper:
    """Class representing word objects"""

    __slots__ = ["db", "philo_id", "object_type", "row", "byte"]

    def __init__(self, id, db, byte):
        self.db = db
        self.philo_id = id
        self.object_type = "word"
        self.row = None
        self.byte = byte

    @property
    def parent(self):
        """Calculates and returns the parent value."""
        return self.philo_id.split()[:6] + ["0"]

    def __getitem__(self, key):
        if key == "parent":
            return self.parent
        return ""

    def __getattr__(self, name):
        return self[name]
