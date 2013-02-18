import re
import cgi
import sys
import struct
import sqlite3 
import HitList

tests = ['hello','"hello"','hi|hello','hi|"hello"','1-5','hello-hi','1-5|"hi|hello"','NULL',"NOT NULL",'hi|NULL', 'hello NOT hi','"hello" NOT hi',"NOT 1-5|hi","1-5 NOT 4", "hello NOT"]
pattern = r'(\"[^\"]*?\")|([|])|(.*?\-.*?)|(.+)'

patterns = [("QUOTE",r'".*?"'),
            ("NOT"," ?NOT "),
            ('OR',r'\|'),
            ('RANGE',r'[^|! ]*?\-[^|! ]*'),
            ('NULL',r'NULL'),
            ('TERM',r'[^|!]+')]

def make_clause(column,tokens):
    clauses = ""
    vars = []
    conj = "AND"
    neg = False
    for t in tokens:
        if t[0] == "NOT":
            neg = True
            clause = ""
        elif t[0] == "QUOTE":
            if neg:
                clause = "%s != ?" % (column)
                vars.append(t[1][1:-1])
            else:
                clause = "%s == ?" % (column)
                vars.append(t[1][1:-1])
        elif t[0] == "OR":
            if neg:
                conj = "AND"
            else:
                conj = "OR"
        elif t[0] == "RANGE":
            lower,upper = t[1].split("-")
            if neg:
                clause = "%s <= ? OR %s >= ?" % (column,column)
                vars.append(lower)
                vars.append(upper)
            else:
                clause = "%s >= ? AND %s <= ?" % (column,column)
                vars.append(lower)
                vars.append(upper)
        elif t[0] == "NULL":
            if neg:
                clause = "%s IS NOT NULL" % column
            else:
                clause = "%s IS NULL" % column
        elif t[0] == "TERM":
            if neg:
                clause = "%s NOT LIKE ?" % (column)
                vars.append("%" + t[1] + "%")
            else:
                clause = "%s LIKE ?" % (column)
                vars.append("%" + t[1] + "%")
                            
        if clause and clauses:
            clauses += " " + conj + " " + clause
            clause = ""
            if conj == "OR":
                conj = "AND"
        elif clause:
            clauses += clause
            clause = ""

    return (clauses,vars)

def parse(column,orig):
        temp = orig[:]
        temp_result = []
        length = len(temp)
        while len(temp) > 0:
            for pattern in patterns:
                r = re.match(pattern[1],temp)
                if r:
                    if pattern[0] == "TERM":
                        notscan = re.match("(.*?)( NOT )",r.group())
                        if notscan:
                            temp_result.append(("TERM",notscan.group(1)))
                            temp_result.append(("NOT"," NOT "))
                            temp = temp[notscan.end():]
                        else:
                            temp_result.append((pattern[0],r.group())),
                            temp = temp[r.end():]
                    else:
                        temp_result.append((pattern[0],r.group())),
                        temp = temp[r.end():]
                    break
            else:
                break
        return make_clause(column,temp_result)

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

def query_lowlevel(db,param_dict):
    vars = []
    clauses = []
    for column,values in param_dict.items():
        for v in values:
            clause,some_vars = parse(column,v)
            clauses.append(clause)
            vars += some_vars
    if clauses:
        query = "SELECT philo_id FROM toms WHERE " + " AND ".join("(%s)" % c for c in clauses) + ";"
    else:
        query = "SELECT philo_id FROM toms;"
#    vars = [v.decode("utf-8") for v in vars]
    print >> sys.stderr, "%s %% %s" % (query,vars)
    for v in vars:
        print >> sys.stderr, "%s : %s" % (type(v),repr(v))

    results = db.dbh.execute(query,vars)
    return results

def query_recursive(db,param_dict,parent):
    r = query_lowlevel(db,param_dict)
    if parent:
        try:
            outer_hit = next(parent)
        except StopIteration:
            return
        for inner_hit in r:
            while corpus_cmp(str_to_hit(outer_hit["philo_id"]),str_to_hit(inner_hit["philo_id"])) < 0:
                try:
                    outer_hit = next(r)
                except StopIteration:
                    return
            if corpus_cmp(str_to_hit(outer_hit["philo_id"]),str_to_hit(inner_hit["philo_id"])) > 0:
                continue
            else:
                yield inner_hit
    else:
        for row in r:
            yield row

def metadata_query(db,filename,param_dicts):
    prev = None
    for d in param_dicts:
        query = query_recursive(db,d,prev)
        prev = query
    corpus_fh = open(filename,"wb")
    for corpus_obj in query:
        obj_id = [int(x) for x in corpus_obj["philo_id"].split(" ")]
        corpus_fh.write(struct.pack("=7i",*obj_id))
    corpus_fh.close()
    flag = open(filename + ".done","w")
    flag.write("1")
    flag.close()
    return HitList.HitList(filename,0,db)

if __name__ == "__main__":
    results = []
    if len(sys.argv) > 1:
        param_dict = cgi.parse_qs(sys.argv[1])
        db = sqlite3.connect("toms.db")


