#!/usr/bin/python

import time
import sys
from itertools import islice
import sqlite3

obj_dict = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4,
            'para': 5, 'sent': 6, 'word': 7}

class HitWrapper(object):

    def __init__(self, hit, db, obj_type=False, encoding=None):
        self.db = db
        self.hit = hit
        #print >> sys.stderr, self.hit
        self.philo_id = hit
        if obj_type:
            self.type = obj_type
        else:
            try:
                length = len(hit[:hit.index(0)])
            except ValueError:
                length = len(hit)
            if length >= 7: length = 7
            self.type = [k for k in obj_dict if obj_dict[k] == length][0]
        self.row = None
        bytes = []
        words = []
        self.words = []
        if len(list(hit)) == 7:
            self.words.append(WordWrapper(hit,db,self.byte_start))
            page_i = self["page"]
        else:
            parent_id = hit[:6]
            remaining = list(philo_id[7:])
            while remaining:
                self.words += [ parent_id + (remaining.pop(0),) ]
                if remaining:
                    self.bytes.append(remaining.pop(0))
            self.words.sort(key=lambda x:x[-1]) # assumes words in same sent, as does search4
            self.words = [WordWrapper(word,db,byte) for word,byte in zip(self.words,bytes)]

            page_i = self.hit[6]
        page_id = [self.hit[0],0,0,0,0,0,0,0,page_i]
        self.page = PageWrapper(page_id,db)

    def __getitem__(self, key):
        if key in obj_dict:
            return ObjectWrapper(self.hit, self.db, key,encoding=self.encoding)
        else:
            if self.row == None:
                self.row = self.db.get_id_lowlevel(self.philo_id)
            return __safe__lookup(row,key,self.db.encoding)
        
    def __getattr__(self, name):
        if name in obj_dict:
            return ObjectWrapper(self.hit, self.db, name,encoding=self.encoding)
        else:
            if self.row == None:
                self.row = self.db.get_id_lowlevel(self.philo_id)
            return __safe__lookup(row,name,self.db.encoding)
        
    def get_page(self):
        if self.type == "word" and len(list(self.hit)) > 7:
            page_i = self.hit[6]
        else:
            page_i = self["page"]
        if page_i:
            page_id = [self.hit[0],0,0,0,0,0,0,0,page_i]
            return PageWrapper(page_id)
        else:
            return None
           
class ObjectWrapper(object):
    
    def __init__(self, hit, db, obj_type=False, encoding=None):
        self.db = db
        self.hit = hit
        if obj_type:
            self.philo_id = hit[:obj_dict[obj_type]]
            self.type = obj_type
        else:
            self.philo_id = hit
            try:
                length = len(hit[:hit.index(0)])
            except ValueError:
                length = len(hit)
            self.type = [k for k in obj_dict if obj_dict[k] == length][0]
        self.bytes = bytes        
        self.row = None
        self.words = []
        page_i = self["page"]
        page_id = [self.hit[0],0,0,0,0,0,0,0,page_i]
        self.page = PageWrapper(page_id,db)

    def __getitem__(self, key):
        if key in obj_dict:
            return ObjectWrapper(self.hit, self.db, key,encoding=self.encoding)
        else:
            if self.row == None:
                self.row = self.db.get_id_lowlevel(self.philo_id)
            return __safe__lookup(row,key,self.db.encoding)
        
    def __getattr__(self, name):
        if name in obj_dict:
            return ObjectWrapper(self.hit, self.db, name,encoding=self.encoding)
        else:
            if self.row == None:
                self.row = self.db.get_id_lowlevel(self.philo_id)
            return __safe__lookup(row,name,self.db.encoding)

    def get_page(self):
        if self.type == "word" and len(list(self.hit)) > 7:
            page_i = self.hit[6]
        else:
            page_i = self["page"]
        if page_i:
            page_id = [self.hit[0],0,0,0,0,0,0,0,page_i]
            return PageWrapper(page_id)
        else:
            return None
            
class PageWrapper(object):
    def __init__(self,id,db):
        self.db = db
        self.philo_id = id
        self_type = "page"
        self.row = None
        self.bytes = []
        
    def __getitem__(self,key):
        if self.row == None:
            self.row = self.db.get_page(self.philo_id)
        return __safe__lookup(row,key,self.db.encoding)

    def __getattr__(self,name):
        if self.row == None:
            self.row = self.db.get_page(self.philo_id)
        return __safe__lookup(row,name,self.db.encoding)

class WordWrapper(object):
    def __init__(self,id,db,byte):
        self.db = db
        self.philo_id = id
        self.type = "word"
        self.row = None
        self.byte = byte

    def __getitem__(self,key):
        if self.row == None:
            self.row = self.db.get_word(self.philo_id)
        return __safe__lookup(row,key,self.db.encoding)

    def __getattr__(self,name):
        if self.row == None:
            self.row = self.db.get_word(self.philo_id)
        return __safe__lookup(row,name,self.db.encoding)


def __safe__lookup(row,field,encoding="utf-8"):
    metadata = ""
    try: 
        metadata = row[field]
    except:
        pass
    metadata_string = ""
    try: 
        metadata_string = metadata.decode(encoding,"ignore")
    except AttributeError:
        metadata_string = str(metadata).decode(encoding,"ignore")
    return metadata_string