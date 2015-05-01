#!/usr/bin/env python
import re
import os
import sys
import time
import codecs
import struct
from HitWrapper import HitWrapper, ObjectWrapper

class HitList(object):
    def __init__(self,filename,words,dbh,encoding=None,doc=0,byte=6,method="proxy",methodarg = 3):
        self.filename = filename
        self.words = words
        self.method = method
        self.methodarg = methodarg
        self.dbh = dbh
        self.encoding = encoding or dbh.encoding
        if method is not "cooc":
            self.has_word_id = 1
            self.length = 7 + 2 * (words)
        else:
            self.has_word_id = 0 #unfortunately.  fix this next time I have 3 months to spare.
            self.length = methodarg + 1 + (words)
        self.fh = open(self.filename) #need a full path here.
        self.format = "=%dI" % self.length #short for object id's, int for byte offset.
        self.hitsize = struct.calcsize(self.format)
        self.doc = doc
        self.byte = byte
        self.position = 0;
        self.done = False
        #self.hitsize = 4 * (6 + self.words) # roughly.  packed 32-bit ints, 4 bytes each.
        self.update()
        
    def __getitem__(self,n):
        self.update()
        if isinstance(n,slice):
            return self.get_slice(n)
        else:            
            self.readhit(n)
            return HitWrapper(self.readhit(n),self.dbh)

    def get_slice(self,n):
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
            except IndexError,IOError:
                break
            yield HitWrapper(hit,self.dbh)
            slice_position += 1
                
    def __len__(self):
        self.update()
        return self.count
        
    def __iter__(self):
        self.update()
        iter_position = 0
        self.seek(iter_position)
        while True:
            try:
                hit = self.readhit(iter_position)
            except IndexError,IOError:
                break
            yield HitWrapper(hit,self.dbh)
            iter_position += 1

    def finish(self):
        self.update()
        while not self.done:
            time.sleep(.02)
            self.update()

    def seek(self,n):
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
            self.size = os.stat(self.filename).st_size # in bytes
            self.count = self.size / self.hitsize 
            #print >> sys.stderr, "size:%d  count:%d" % (self.size, self.count)

    def finish(self):
        while not self.done:
            self.update()
            time.sleep(0.05)

    def readhit(self,n):
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
            offset = self.hitsize * n;
            #print >> sys.stderr, "reading %d, seeking %d" % (n,offset)
            self.fh.seek(offset)
            self.position = n
        buffer = self.fh.read(self.hitsize)
        self.position += 1
        return(struct.unpack(self.format,buffer))


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
