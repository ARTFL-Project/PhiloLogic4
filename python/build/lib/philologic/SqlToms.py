import re
import os
import sys
import ast
import sqlite3

class SqlToms:
    def __init__(self,dbfile,w):
        self.dbh = sqlite3.connect(dbfile)
        self.dbh.text_factory = str
        self.dbh.row_factory = sqlite3.Row
        self.width = w

    def __contains__(self,item):
        hit_s = hit_to_string(item,self.width)
        c = self.dbh.cursor()
        c.execute("SELECT * FROM toms WHERE philo_id=?;",(hit_s,))
        if c.fetchone():
            return True
        else:
            return False

    def __getitem__(self,item):
        hit_s = hit_to_string(item,self.width)
        c = self.dbh.cursor()
        c.execute("SELECT * FROM toms WHERE philo_id=? LIMIT 1;",(hit_s,))
        return c.fetchone()

    def compound_query(self, *dicts):
        previous = None
        for d in dicts:
            query = self.query(previous,**d)
            previous = query
        return query

    def query(self,corpus=None,**args):
        if not args:
            return
        else:
            qstring = "SELECT * FROM toms WHERE"
            vs = []
            wherecount = 0
            for k,v in args.items():
                if wherecount:
                    qstring += " AND"
                if k == "philo_type":
                    qstring += " %s == ?" % (k)
                    vs.append(v)
                elif v == "[None]":
                    qstring += " %s IS NULL" % (k)                    
                else:
                    qstring += " %s LIKE ?" % (k) # forgot the AND
                    vs.append("%" + v + "%")
                wherecount += 1
            qstring += " ORDER BY philo_seq;"
            print >> sys.stderr, qstring
            c = self.dbh.cursor()
            c.execute(qstring,vs)
            if corpus:
                try:
                    outer_hit = next(corpus)
                except StopIteration:
                    return
                for inner_hit in c:
                    while corpus_cmp(str_to_hit(outer_hit["philo_id"]),str_to_hit(inner_hit["philo_id"])) < 0:
                        try:
                            outer_hit = next(corpus)
                        except StopIteration:
                            return
                    if corpus_cmp(str_to_hit(outer_hit["philo_id"]),str_to_hit(inner_hit["philo_id"])) > 0:
                        continue
                    else:
                        yield inner_hit
            else:
                for row in c:
                    yield row

    def get_documents(self):
        c = self.dbh.cursor()
        c.execute("SELECT * FROM toms WHERE philo_type='doc' ORDER BY philo_seq;")
        for row in c:
            yield row

    def get_children(self,obj):
        #should take object as a list, not string.
        obj_string = hit_to_string(obj,self.width)
        c = self.dbh.cursor()
        c.execute("SELECT * FROM toms WHERE parent=? ORDER BY philo_seq;",(obj_string,))
        for row in c:
            yield row
                
    def get_parent(self,obj):
        parent = obj["parent"]
        if not parent:
            return []
        else:
            p = str_to_hit(parent)
            return self[p]
        
    def get_siblings(self,obj):
        p = self.get_parent(obj)
        if not p:
            return []
        sibs = self.get_children(p)
        return sibs

    def get_prev_next(self,obj):
        current_obj = obj
        prev = None
        while current_obj:
            my_siblings = list(self.get_siblings(current_obj))
            if not my_siblings:
                break
            my_position = my_siblings.index(current_obj)
            if my_position > 0: # if we have a sibling to the left:
                current_obj = my_siblings[my_position - 1]
                prev = current_obj
                while True: # descend to its RIGHTmost leaf
                    my_children = list(self.get_children(current_obj))
                    if my_children:
                        current_obj = my_children[-1]
                        prev = current_obj
                    else:
                        break
                break
            else: # go up a level
                current_obj = self.get_parent(current_obj)
                
        #setup for next seek.  Mostly the same.
        current_obj = obj
        next = None
        while current_obj:
            my_siblings = list(self.get_siblings(current_obj))
            if not my_siblings:
                break
            my_position = my_siblings.index(current_obj)
            if my_position < len(my_siblings) - 1: # if we have a sibling on the right
                current_obj = my_siblings[my_position + 1]
                next = current_obj
                while True: # descend to its LEFTmost leaf
                    my_children = list(self.get_children(current_obj))
                    if my_children:
                        current_obj = my_children[0]
                        next = current_obj
                    else:
                        break
                break
            else:
                current_obj = self.get_parent(current_obj)
    
        return prev,next

    def mktoms_sql(self,file_in):
        known_fields = []
        db = self.dbh
        db.text_factory = str
        db.execute("CREATE TABLE IF NOT EXISTS toms (philo_type,philo_name,philo_id,philo_seq);")
        db.execute("CREATE INDEX type_index ON toms(philo_type);")
        db.execute("CREATE INDEX id_index ON toms(philo_id);")
        s = 0
        for line in open(file_in):
            (philo_type,philo_name,id,attrib) = line.split("\t",3)
            fields = id.split(" ",8)
            if len(fields) == 9: 
                philo_id = " ".join(fields[:7])
                raw_attr = attrib
                #print raw_attr
                r = {}
                r["philo_type"] = philo_type
                r["philo_name"] = philo_name
                r["philo_id"] = philo_id
                r["philo_seq"] = s
                # I should add philo_parent here.  tricky to keep track of though.
                attr = ast.literal_eval(raw_attr)
                #print attr
                for k in attr:
                    if k not in known_fields:
                        print k
                        db.execute("ALTER TABLE toms ADD COLUMN %s;" % k) 
                        # it seems like i can't safely interpolate column names. ah well.
                        known_fields.append(k)
                    r[k] = attr[k]
                rk = []
                rv = []
                for k,v in r.items():
                    rk.append(k)
                    rv.append(v)
                ks = "(%s)" % ",".join(x for x in rk)
#                print ks
#                print repr(rv)
                insert = "INSERT INTO toms %s values (%s);" % (ks,",".join("?" for i in rv))
                db.execute(insert,rv)
                s += 1
        db.commit()

    def mkpages_sql(self,file_in):
        known_fields = []
        db = self.dbh
        db.text_factory = str
        db.execute("CREATE TABLE IF NOT EXISTS toms (philo_type,philo_name,philo_id,philo_seq);")
        db.execute("CREATE INDEX type_index ON toms(philo_type);")
        db.execute("CREATE INDEX id_index ON toms(philo_id);")
        s = 0
        for line in open(file_in):
            (philo_type,philo_name,id,attrib) = line.split("\t",3)
            fields = id.split(" ",8)
            if len(fields) == 9: 
                philo_id = " ".join((fields[0],fields[8]))
                raw_attr = attrib
                #print raw_attr
                r = {}
                r["philo_type"] = philo_type
                r["philo_name"] = philo_name
                r["philo_id"] = philo_id
                r["philo_seq"] = s
                # I should add philo_parent here.  tricky to keep track of though.
                attr = ast.literal_eval(raw_attr)
                #print attr
                for k in attr:
                    if k not in known_fields:
                        print k
                        db.execute("ALTER TABLE toms ADD COLUMN %s;" % k) 
                        # it seems like i can't safely interpolate column names. ah well.
                        known_fields.append(k)
                    r[k] = attr[k]
                rk = []
                rv = []
                for k,v in r.items():
                    rk.append(k)
                    rv.append(v)
                ks = "(%s)" % ",".join(x for x in rk)
#                print ks
#                print repr(rv)
                insert = "INSERT INTO toms %s values (%s);" % (ks,",".join("?" for i in rv))
                db.execute(insert,rv)
                s += 1
        db.commit()
        
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

def str_to_hit(string):
    return [int(x) for x in string.split(" ")]

def obj_cmp(x,y):
    for a,b in zip(x,y):
        if a < b:
            return -1
        if a > b:
            return 1
    else:
        return 0

def corpus_cmp(x,y):
    if 0 in x:
        depth = x.index(0)
    else:
        depth = len(x)
    return obj_cmp(x[:depth],y[:depth])

def obj_contains(x,y):
    pass

if __name__ == "__main__":
    import sys
    mktoms_sql(sys.argv[1],sys.argv[2])
    
