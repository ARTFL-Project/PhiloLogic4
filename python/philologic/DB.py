import os,sys
import hashlib
import struct
import sqlite3
import re
import MetadataQuery
import HitList
import sys
import QuerySyntax
from HitWrapper import HitWrapper
from philologic import Query,shlax
from Config import Config, db_locals_defaults, db_locals_header

def hit_to_string(hit,width):
    if isinstance(hit,sqlite3.Row):
        hit = hit["philo_id"]
    if isinstance(hit,str):
        hit = [int(x) for x in hit.split(" ")]
    if isinstance(hit,int):
        hit = [hit]
    if len(hit) > width:
        hit = hit[:width]
    pad = width - len(hit)
    hit_string = " ".join(str(h) for h in hit)
    hit_string += "".join(" 0" for n in range(pad))
    return hit_string

class DB:
    def __init__(self,dbpath,width = 7,encoding="utf-8"):
        self.path = dbpath
        self.dbh = sqlite3.connect(dbpath + "/toms.db",width)
        self.dbh.text_factory = str
        self.dbh.row_factory = sqlite3.Row
        self.width = width
        self.encoding="utf-8"
#        self.locals = {}
        self.locals = Config(dbpath + "/db.locals.py", db_locals_defaults, db_locals_header)
        # try:
        #     execfile(dbpath + "/db.locals.py",globals(),self.locals)
        # except IOError:
        #     pass
        # if "metadata_fields" not in self.locals:
        #     self.locals["metadata_fields"] = ["author","title","date","who","head"]
        # if "metadata_hierarchy" not in self.locals:
        #     self.locals["metadata_hierarchy"] = [ ["author","title","date"],["head"],["who"] ]
        # if "metadata_types" not in self.locals:
        #     self.locals["metadata_types"] = {"author":"doc","title":"doc","date":"doc","head":"div","who":"para"}
        # if "normalized_fields" not in self.locals:
        #     self.locals["normalized_fields"] = []

    def __getitem__(self,item):
        hit = self.get_id_lowlevel(item)
        hit = [int(x) for x in hit["philo_id"].split(" ")]
        return HitWrapper(hit,self)

    def get_id_lowlevel(self,item):
        hit_s = hit_to_string(item,self.width)
        c = self.dbh.cursor()
        c.execute("SELECT * FROM toms WHERE philo_id=? LIMIT 1;",(hit_s,))
        return c.fetchone()

    def get_word(self,item):
        word_s = hit_to_string(item,self.width)
        c = self.dbh.cursor()
        c.execute("SELECT * FROM words WHERE philo_id=? LIMIT 1;",(word_s,))
        return c.fetchone()

    def get_page(self,item):
        #print >> sys.stderr, "PAGE_ITEM", item
        page_id_s = " ".join(str(s) for s in item)
        #print >> sys.stderr, "PAGE_ITEM_STRING", page_id_s
        c = self.dbh.cursor()
        c.execute("SELECT * FROM pages WHERE philo_id=? LIMIT 1;",(page_id_s,))
        return c.fetchone()

    def get_all(self,philo_type="doc"):
        """ get all objects of type philo_type """
        hash = hashlib.sha1()
        hash.update(self.path)
        hash.update(philo_type)
        all_hash = hash.hexdigest()
        all_file = self.path + "/hitlists/" + all_hash + ".hitlist"
        if not os.path.isfile(all_file):
            #write out the corpus file
            return MetadataQuery.metadata_query(self,all_file,[{"philo_type":['"%s"' % philo_type]}])
        else:
            return HitList.HitList(all_file,0,self)

    def query(self,qs="",method="",method_arg="",limit="",**metadata):
        """query the PhiloLogic database"""
        method = method or "proxy"
        if isinstance(method_arg,str):
            try:
                method_arg = int(method_arg)
            except:
                if method == "cooc" or method == "sentence":
                    method_arg = 6
                else:
                    method_arg = 0

        if isinstance(limit,str):
            try:
                limit = int(limit)
            except:
                limit = 10000000

        hash = hashlib.sha1()
        hash.update(self.path)
        has_metadata = False
        corpus_file = None

        for key,value in metadata.items():
            if isinstance(value,str):
                if value == "":
                    pass
                else:
                    value = [value]
                    metadata[key] = value
            value = [v for v in value if v]
            if value:
                has_metadata = True
                hash.update("%s=%s" % (key,"|".join(value)))

        if has_metadata:
            corpus_hash = hash.hexdigest()
            corpus_file = self.path + "/hitlists/" + corpus_hash + ".hitlist"
            corpus_width = 7

            if not os.path.isfile(corpus_file):
                # before we query, we need to figure out what type each parameter belongs to,
                # and sort them into a list of dictionaries, one for each type.
                metadata_dicts = [{} for level in self.locals["metadata_hierarchy"]]
#                print >> sys.stderr, "querying %s" % repr(metadata.items())
                for k,v in metadata.items():
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
                        metadata_dicts.append( {"philo_id":metadata["philo_id"]} )
                corpus = MetadataQuery.metadata_query(self,corpus_file,metadata_dicts)
            else:
#                print >> sys.stderr, "cached @ %s" % corpus_file
                corpus = HitList.HitList(corpus_file,0,self)
                corpus.finish()
            #print >> sys.stderr, "corpus file of length %d" % len(corpus)
            if len(corpus) == 0:
                return corpus
        else:
            corpus = None
        if qs:
#            words_per_hit = len(qs.split(" "))
#            words_per_hit = len(qs.split("\n\n"))
            hash.update(qs)
            hash.update(method)
            hash.update(str(method_arg))
            hash.update(str(limit))
            search_hash = hash.hexdigest()
            search_file = self.path + "/hitlists/" + search_hash + ".hitlist"
            if not os.path.isfile(search_file):
                return Query.query(self,qs,corpus_file,self.width,method,method_arg,limit,filename=search_file)
            else:
                parsed = QuerySyntax.parse_query(qs)
                grouped = QuerySyntax.group_terms(parsed)
                split = Query.split_terms(grouped)
                words_per_hit = len(split)
#                parsed = QuerySyntax.parse_query(qs)
#                parsed_split = []
#                for label,token in parsed:
#                    l,t = label,token
#                    if l == "QUOTE":
#                        subtokens = t[1:-1].split(" ")
#                        parsed_split += [("QUOTE_S",sub_t) for sub_t in subtokens if sub_t]
#                    else:
#                        parsed_split += [(l,t)]
#                command = Query.format_parsed_query(parsed_split,self)
#                words_per_hit = len(command.split("\n\n"))

                return HitList.HitList(search_file,words_per_hit,self)
        else:
            if corpus:
                return corpus
            else:
                return self.get_all("doc")
