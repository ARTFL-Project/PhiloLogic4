#!/usr/bin/env python
import re
import os
import sys
import time
import codecs
import struct
from HitWrapper import HitWrapper, ObjectWrapper
from utils import smash_accents

obj_dict = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4, 'para': 5, 'sent': 6, 'word': 7}


class HitList(object):
    def __init__(self,
                 filename,
                 words,
                 dbh,
                 encoding=None,
                 doc=0,
                 byte=6,
                 method="proxy",
                 methodarg=3,
                 sort_order=None,
                 raw=False):
        self.filename = filename
        self.words = words
        self.method = method
        self.methodarg = methodarg
        self.sort_order = sort_order
        if self.sort_order == ["rowid"]:
            self.sort_order = None
        self.raw = raw  # if true, this return the raw hitlist consisting of a list of philo_ids
        self.dbh = dbh
        self.encoding = encoding or dbh.encoding
        if method is not "cooc":
            self.has_word_id = 1
            self.length = 7 + 2 * (words)
        else:
            self.has_word_id = 0  #unfortunately.  fix this next time I have 3 months to spare.
            self.length = methodarg + 1 + (words)
        self.fh = open(self.filename)  #need a full path here.
        self.format = "=%dI" % self.length  #short for object id's, int for byte offset.
        self.hitsize = struct.calcsize(self.format)
        self.doc = doc
        self.byte = byte
        self.position = 0
        self.done = False
        self.update()

        if self.sort_order:
            metadata_types = set([dbh.locals["metadata_types"][i] for i in self.sort_order])
            if "div" in metadata_types:
                metadata_types.remove("div")
                metadata_types.union(set(["div1", "div2", "div3"]))
            c = self.dbh.dbh.cursor()
            query = "select * from toms where "
            params = []
            for metadata_type in metadata_types:
                params.append('philo_type="%s"' % metadata_type)
            query += " and ".join(params) + " and "
            order_params = []
            for s in self.sort_order:
                order_params.append('%s is not null' % s)
            query += " and ".join(order_params)
            c.execute(query)
            metadata = {}
            for i in c.fetchall():
                doc_id = int(i['philo_id'].split()[0])
                metadata[doc_id] = [smash_accents(i[m]) for m in sort_order]
            self.sorted_hitlist = []
            iter_position = 0
            self.seek(iter_position)
            while True:
                try:
                    hit = self.readhit(iter_position)
                except IndexError, IOError:
                    break
                self.sorted_hitlist.append(hit)
                iter_position += 1
            self.sorted_hitlist.sort(key=lambda x: metadata[x[0]])


    def __getitem__(self, n):
        if self.sort_order:
            return self.get_slice(n)
        else:
            self.update()
            if isinstance(n, slice):
                return self.get_slice(n)
            else:
                if self.raw:
                    return self.readhit(n)
                else:
                    self.readhit(n)
                    return HitWrapper(self.readhit(n), self.dbh)

    def get_slice(self, n):
        if self.sort_order:
            try:
                for hit in self.sorted_hitlist[n]:
                    yield HitWrapper(hit, self.dbh)
            except IndexError:
                pass
        else:
            self.update()
            #need to handle negative offsets.
            slice_position = n.start or 0
            self.seek(slice_position)
            while True:
                if n.stop is not None:
                    if slice_position >= n.stop:
                        break
                try:
                    hit = self.readhit(slice_position)
                except IndexError, IOError:
                    break
                if self.raw:
                    yield hit
                else:
                    yield HitWrapper(hit, self.dbh)
                slice_position += 1

    def __len__(self):
        self.update()
        return self.count

    def __iter__(self):
        if self.sort_order:
            for hit in self.sorted_hitlist:
                yield HitWrapper(hit, self.dbh)
        else:
            self.update()
            iter_position = 0
            self.seek(iter_position)
            while True:
                try:
                    hit = self.readhit(iter_position)
                except IndexError, IOError:
                    break
                if self.raw:
                    yield hit
                else:
                    yield HitWrapper(hit, self.dbh)
                iter_position += 1

    def finish(self):
        self.update()
        while not self.done:
            time.sleep(.02)
            self.update()

    def seek(self, n):
        if self.position == n:
            pass
        else:
            while n >= len(self):
                if self.done:
                    raise IndexError
                else:
                    time.sleep(.05)
                    self.update()
            offset = self.hitsize * n
            #print >> sys.stderr, "seeking %d:%d" % (n,offset)
            self.fh.seek(offset)
            self.position = n

    def update(self):
        #Since the file could be growing, we should frequently check size/ if it's finished yet.
        if self.done:
            pass
        else:
            try:
                os.stat(self.filename + ".done")
                self.done = True
            except OSError:
                pass
            self.size = os.stat(self.filename).st_size  # in bytes
            self.count = self.size / self.hitsize
            #print >> sys.stderr, "size:%d  count:%d" % (self.size, self.count)

    def finish(self):
        while not self.done:
            self.update()
            time.sleep(0.05)

    def readhit(self, n):
        #reads hitlist into buffer, unpacks
        #should do some work to read k at once, track buffer state.
        self.update()
        while n >= len(self):
            if self.done:
                raise IndexError
            else:
                time.sleep(.05)
                self.update()
        if n != self.position:
            offset = self.hitsize * n
            #print >> sys.stderr, "reading %d, seeking %d" % (n,offset)
            self.fh.seek(offset)
            self.position = n
        buffer = self.fh.read(self.hitsize)
        self.position += 1
        return (struct.unpack(self.format, buffer))


# TODO: check if we still need this...
class CombinedHitlist(object):
    """A combined hitlists used for binding collocation hits"""

    def __init__(self, *hitlists):
        self.combined_hitlist = []
        # sentence_ids = set()
        # for hit in sorted(chain(*hitlists), key=lambda x: x.date):
        #     sentence_id = hit.philo_id[:6]
        #     if sentence_id not in sentence_ids:
        #         self.combined_hitlist.append(hit)
        #         sentence_ids.add(sentence_id)
        from collections import defaultdict
        sentence_counts = defaultdict(int)
        for pos, hitlist in enumerate(hitlists):
            max_sent_count = 2
            for hit in hitlist:
                sentence_id = repr(hit.philo_id[:6])
                if sentence_id not in sentence_counts or sentence_counts[sentence_id] == max_sent_count:
                    self.combined_hitlist.append(hit)
                    sentence_counts[sentence_id] += 1

        self.done = True

    def __len__(self):
        return len(self.combined_hitlist)

    def __getitem__(self, key):
        return self.combined_hitlist[key]

    def __getattr__(self, name):
        return self.combined_hitlist[name]


class WordPropertyHitlist(object):
    def __init__(self, hitlist):
        self.done = True
        self.hitlist = hitlist

    def __getitem__(self, key):
        return self.hitlist[key]

    def __getattr__(self, name):
        return self.hitlist[name]

    def __len__(self):
        return len(self.hitlist)


class NoHits(object):
    def __init__(self):
        self.done = True

    def __len__(self):
        return 0

    def __getitem__(self, item):
        return ''

    def __iter__(self):
        return ''

    def finish(self):
        return

    def update(self):
        return
