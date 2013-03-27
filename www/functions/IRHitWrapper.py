#!/usr/bin/env python

from philologic.HitWrapper import ObjectWrapper


obj_dict = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4, 
            'para': 5, 'sent': 6, 'word': 7}
        

class HitWrapper(object):

    def __init__(self, hit, db, bytes, obj_type=False, encoding=None):
        self.db = db
        self.hit = hit
        self.philo_id = hit
        self.bytes = bytes
        self.encoding = encoding
        if obj_type:
            self.type = obj_type
        else:
            try:
                length = len(hit[:hit.index(0)])
            except ValueError:
                length = len(hit)
            if length >= 7: length = 7
            self.type = [k for k in obj_dict if obj_dict[k] == length][0]

    def __getitem__(self, key):
        if key in obj_dict:
            return ObjectWrapper(self.hit, self.db, obj_type=key,encoding=self.encoding)
        else:
            return self.__metadata_lookup(key)
    
    def __getattr__(self, name):
        if name in obj_dict:
            return ObjectWrapper(self.hit, self.db, obj_type=name,encoding=self.encoding)
        else:
            return self.__metadata_lookup(name)
        
    def __metadata_lookup(self, field):
        width = 7
        philo_id = self.philo_id[:width]
        metadata = None
        while width:
            try:
                metadata = self.db.get_id_lowlevel(philo_id[:width])[field]
            except (TypeError,IndexError):
                width -= 1
                continue
            if metadata != None:
                break
            width -= 1
        if metadata == None:
            metadata = ''
        if self.db.encoding:
            try:
                return metadata.decode(self.db.encoding, 'ignore')
            except AttributeError:
                ## if the metadata is an integer
                return metadata
        else:
            return metadata
