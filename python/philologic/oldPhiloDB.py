import os,sys
import hashlib
import struct
import re
from philologic import Query,SqlToms,HitList,shlax
              
def make_cite(db,hit,url):
    doc = db[hit[0]]
    div1 = db[hit[:2]]
    div2 = db[hit[:3]]
    div3 = db[hit[:4]]
    para = db[hit[:5]]
    page_id = [hit[0]] + list(hit[6:7])
    print >> sys.stderr, "hit %s" % str(hit)
    page = db.pages[page_id]
    r = ""
    r += "<a class='philologic_cite' href='%s' id='%s'>" % (url,hit)

    if "author" in doc.keys():
        r += ("<span class='philologic_property' title='author'>%s</span>, " % doc["author"])
    if "title" in doc.keys():
        r += ("<span class='philologic_property' title='title'>%s</span> " % doc["title"])
    if "date" in doc.keys():
        r += ("<span class='philologic_property' title='date'>(%s)</span>" % doc["date"])
    if div2 and "head" in div2.keys() and div2["head"]:
        r += ("<span class='philologic_property' title='head'> %s</span>" % div1["head"])
    elif div1 and "head" in div1.keys() and div1["head"]:
        r += ("<span class='philologic_property' title='head'> %s</span>" % div1["head"])
    elif div2 and "headword" in div2.keys() and div2["headword"]:
        r += ("<span class='philologic_property' title='headword'> %s</span>" % div1["headword"])
    elif div1 and "headword" in div1.keys() and div1["headword"]:
        r += ("<span class='philologic_property' title='headword'> %s</span>" % div1["headword"])
    if div1 and "articleAuthor" in div1.keys() and div1["articleAuthor"] != "unknown":
        r += ("<span class='philologic_property' title='articleAuthor'>- %s</span>" % div1["articleAuthor"])
    if div1 and "normClass" in div1.keys() and div1["normClass"] != "unclassified":
        r += ("<span class='philologic_property' title='normClass'> [%s]</span>" % div1["normClass"])
    elif div1 and "normalizedClass" in div1.keys() and div1["normalizedClass"] != "unclassified":
        r += ("<span class='philologic_property' title='normalizedClass'> [%s]</span>" % div1["normalizedClass"])

    if page:
        r += " " + page["n"]

    r += ("</a>\n")
    return r


def format_stream(text,start = 0,offsets = []):
    byte_offsets = offsets[:]
    need_l_trim = re.search("^[^<]*?>",text)
    if need_l_trim:
        l_trim_off = need_l_trim.end(0)
        text = text[l_trim_off:]
    else:
        l_trim_off = 0
        
    need_r_trim = re.search("<[^>]*?$",text)
    if need_r_trim:
        r_trim_off = need_r_trim.start(0)
        text = text[:r_trim_off]
    else:
        r_trim_off = 0
        
    start_point = start + l_trim_off
    stream = shlax.parsestring(text)
    output = ""
    for node in stream:        
        if node.type == "text":
            while byte_offsets and node.start + start_point + len(node.content) > byte_offsets[0]:
                word_start = byte_offsets[0] - (node.start + start_point)
                output += node.content[:word_start]
                output += "<span class='hilite'>"
                rest = node.content[word_start:]
                word_end = re.search("[\s\.,;?!'\"]|$",rest).start(0)
                output += rest[:word_end]
                output += "</span>"
                byte_offsets.pop(0)
                node.content = rest[word_end:]
                node.start = node.start + word_start + word_end
            output += node.content            
        if node.type == "StartTag" and (node.name == "l" or node.name == "speaker" or node.name == "ab"):
            output += "<br/>"
        elif node.type == "StartTag" and node.name == "p":
            output += "<p/>"

    return output

class PhiloDB:
    def __init__(self,dbpath,width = 7):
        self.path = dbpath
        self.toms = SqlToms.SqlToms(dbpath + "/toms.db",width)
        self.width = width
        self.locals = {}
        self.pages = SqlToms.SqlToms(dbpath + "/pages.db",2)
        try:
            execfile(dbpath + "/db.locals.py",globals(),self.locals)
        except IOError:
            pass
        if "metadata_fields" not in self.locals: 
            self.locals["metadata_fields"] = ["author","title","date","who","head"]
        if "metadata_hierarchy" not in self.locals:
            self.locals["metadata_hierarchy"] = [ ["author","title","date"],["head"],["who"] ]
        if "metadata_types" not in self.locals:
            self.locals["metadata_types"] = {"author":"doc","title":"doc","date":"doc","head":"div","who":"para"}            
        if "make_cite" not in self.locals:
            self.locals["make_cite"] = make_cite
        if "format_stream" not in self.locals:
            self.locals["format_stream"] = format_stream
        if "conc_width" not in self.locals:
            self.locals["conc_width"] = 400

    def __getitem__(self,n):
        return self.toms[n]

    def metadata_query(self,**metadata):
        template = [{} for level in self.locals["metadata_hierarchy"]]
        for k,v in metadata.items():
            for i, params in enumerate(self.locals["metadata_hierarchy"]):
                if v and (k in params):
                    template[i][k] = v
                    if k in self.locals["metadata_types"]:
                        template[i]["philo_type"] = self.locals["metadata_types"][k]
        result = None
        for t in template:
            if t:                
                result = self.toms.query(corpus=result,**t)
        return result

    def query(self,qs,method=None,method_arg=0,limit=1000000,**metadata):
        hashable = (qs,method,method_arg,tuple(metadata.items()))
        hash = hashlib.sha1()
        hash.update(self.path)
        hash.update(qs)
        hash.update(method or "")
        hash.update(method_arg or "")
        hash.update(str(limit))
        for key,value in metadata.items():
            hash.update(str(key))
            hash.update(str(value))
        hex_hash = hash.hexdigest()
        print >> sys.stderr,"%s hashes to %s" % (hashable,hex_hash)
        #check here to see if the query is cached.
        hfile = "/var/lib/philologic/hitlists/" + hex_hash + ".hitlist"
        words_per_hit = len(qs.split(" "))
        if os.path.isfile(hfile):
            print >> sys.stderr, "%s cached already" % (hashable,)
            return HitList.HitList(hfile,words_per_hit) #debug.
        corpus_file = None
        corpus_size = self.width
        corpus_count = 0
        print >> sys.stderr, "metadata = %s" % repr(metadata)
        if metadata and [v for k,v in metadata.items() if v]: # kind of a hack.  should have better handling of null metadata.
            corpus_file = "/var/lib/philologic/hitlists/" + hex_hash + ".corpus"
            corpus_fh = open(corpus_file,"wb")
            for c_obj in self.metadata_query(**metadata):
                c_id = [int(x) for x in c_obj["philo_id"].split(" ")]
                corpus_fh.write(struct.pack("=7i",*c_id))
                corpus_count += 1
            corpus_fh.close()
            if corpus_count == 0: return []
        print >> sys.stderr, "%d metadata objects" % corpus_count
        return Query.query(self.path,qs,corpus_file,corpus_size,method,method_arg,limit,filename=hfile)
        
    def word_search(self,qs,*metadata_dicts,**options):
        hash = hashlib.sha1()
        hash.update(self.path)
        hash.update(qs)
        method = options.get("method","")
        method_arg = options.get("method_arg","")
        limit = options.get("limit","")
        hash.update(method)
        hash.update(method_arg)
        hash.update(limit)
        for metadata_level in metadata_dicts:
            for k,v in metadata_level.items():
                hash.update(k)
                hash.update(v)
        hex_hash = hash.hexdigest()
#        print >> sys.stderr, "('%s' %s %d %s )hashes to %s" % (qs,method,method_arg,repr(metadata_dicts),hex_hash)
        hfile = "/var/lib/philologic/hitlists/" + hex_hash + ".hitlist"
        words_per_hit = len(qs.split(" "))
        if os.path.isfile(hfile):
            return HitList.HitList(hfile,words_per_hit) #debug.
        corpus_file = None
        corpus_size = self.width
        corpus_count = 0
 #       print >> sys.stderr, "metadata = %s" % repr(metadata)
        if metadata_dicts:
            corpus_file = "/var/lib/philologic/hitlists/" + hex_hash + ".corpus"
            corpus_fh = open(corpus_file,"wb")
            for c_obj in self.toms.compound_query(*metadata_dicts):
                c_id = [int(x) for x in c_obj["philo_id"].split(" ")]
                corpus_fh.write(struct.pack("=7i",*c_id))
                corpus_count += 1
            corpus_fh.close()
            if corpus_count == 0: return []
  #      print >> sys.stderr, "%d metadata objects" % corpus_count
        return Query.query(self.path,qs,corpus_file,corpus_size,filename=hfile,**options)

    def metadata_search(self,*metadata_dicts):
        pass
        
    def ancestors(self,object):
        """Analyze a single object id and return all objects that are direct ancestors of it."""
        print >> sys.stderr, object
        if isinstance(object,str) or isinstance(object,unicode):
            object = object.split(" ")
        elif "philo_id" in object:
            object = object["philo_id"].split(" ")
        r = []
        object = list(object)
        for n in range(1,len(object) + 1):
            print >> sys.stderr, r
            print >> sys.stderr, object
            ancestor = object[:(n)]
            ancestor.extend([0 for i in range(len(object) - n)])
            print >> sys.stderr, ancestor
            r.append(tuple(ancestor))
        return r
