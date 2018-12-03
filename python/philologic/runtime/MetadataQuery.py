

import os
import sqlite3
import struct
import subprocess
import sys
import unicodedata

from . import HitList
from .HitList import NoHits
from .QuerySyntax import group_terms, parse_query

os.environ["PATH"] += ":/usr/local/bin/"


def metadata_query(db, filename, param_dicts, sort_order, raw_results=False):
    """Prepare and execute SQL metadata query."""
    if db.locals["debug"]:
        print("METADATA_QUERY:", param_dicts, file=sys.stderr)
    prev = None
    for d in param_dicts:
        query = query_recursive(db, d, prev, sort_order)
        prev = query
    try:
        corpus_fh = open(filename, "wb")
        for corpus_obj in query:
            obj_id = [int(x) for x in corpus_obj["philo_id"].split(" ")]
            corpus_fh.write(struct.pack("=7i", *obj_id))
        corpus_fh.close()
    except Exception as e:
        print(str(e), file=sys.stderr)
        # should clean up file
        flag = open(filename + ".done", "w")
        flag.write("1")
        flag.close()
        return NoHits()
    flag = open(filename + ".done", "w")
    flag.write("1")
    flag.close()
    return HitList.HitList(filename, 0, db, raw=raw_results, sort_order=sort_order)


def query_recursive(db, param_dict, parent, sort_order):
    #    print >> sys.stderr, "query_recursive:",param_dict,parent
    r = query_lowlevel(db, param_dict, sort_order)
    if parent:
        try:
            outer_hit = next(parent)
        except StopIteration:
            return
        for inner_hit in r:
            #            print >> sys.stderr, "corpus_cmp:",outer_hit["philo_id"], inner_hit["philo_id"]
            while corpus_cmp(str_to_hit(outer_hit["philo_id"]), str_to_hit(inner_hit["philo_id"])) < 0:
                try:
                    outer_hit = next(parent)
                except StopIteration:
                    return
            if corpus_cmp(str_to_hit(outer_hit["philo_id"]), str_to_hit(inner_hit["philo_id"])) > 0:
                continue
            else:
                yield inner_hit
    else:
        for row in r:
            yield row


def query_lowlevel(db, param_dict, sort_order):
    vars = []
    clauses = []
    for column, values in list(param_dict.items()):
        norm_path = db.path + "/frequencies/normalized_" + column + "_frequencies"
        for v in values:
            parsed = parse_query(v)
            if db.locals["debug"]:
                print("METADATA_TOKENS:", parsed, file=sys.stderr)
            grouped = group_terms(parsed)
            if db.locals["debug"]:
                print("METADATA_SYNTAX GROUPED:", grouped, file=sys.stderr)
            expanded = expand_grouped_query(grouped, norm_path)
            if db.locals["debug"]:
                print("METADATA_SYNTAX EXPANDED:", expanded, file=sys.stderr)
            sql_clause = make_grouped_sql_clause(expanded, column, db)
            if db.locals["debug"]:
                print("SQL_SYNTAX:", sql_clause, file=sys.stderr)
            clauses.append(sql_clause)
    if not sort_order:
        sort_order = ["rowid"]
    if clauses:
        query = (
            "SELECT philo_id FROM toms WHERE "
            + " AND ".join("(%s)" % c for c in clauses)
            + " order by %s;" % ", ".join(sort_order)
        )
    else:
        query = "SELECT philo_id FROM toms order by %s;" % ", ".join(sort_order)
    if db.locals["debug"]:
        print("INNER QUERY: ", "%s %% %s" % (query, vars), sort_order, file=sys.stderr)
    results = db.dbh.execute(query, vars)
    return results


def expand_grouped_query(grouped, norm_path):
    expanded = []
    pure = True
    # first test to see if this is a "pure" query, which can be entirely evaluated in egrep
    # this requires that it is only AND and OR's, for now--I may be able to add the others later
    for group in grouped:
        for kind, token in group:
            if kind == "RANGE" or kind == "NULL":
                pure = False
    if pure:
        # will implement this later
        pass
    for group in grouped:
        expanded_group = []
        for kind, token in group:
            if kind == "TERM":
                norm_term = token.lower()
                norm_term = [c for c in unicodedata.normalize("NFKD", norm_term) if not unicodedata.combining(c)]
                norm_term = "".join(norm_term)
                expanded_terms = metadata_pattern_search(norm_term, norm_path)
                if expanded_terms:
                    expanded_tokens = [("QUOTE", '"' + e + '"') for e in expanded_terms]
                    fully_expanded_tokens = []
                    first = True
                    for e in expanded_tokens:
                        if first:
                            first = False
                        else:
                            fully_expanded_tokens.append(("OR", "|"))
                        fully_expanded_tokens.append(e)
                else:  # if we have no matches, just put an inexact match in as placeholder.  Will fail later.
                    fully_expanded_tokens = [("QUOTE", '"' + norm_term + '"')]
                expanded_group.extend(fully_expanded_tokens)
            else:
                if kind == "NOT":
                    if expanded_group:
                        expanded.append(expanded_group)
                    expanded_group = [(kind, token)]
                elif kind != "OR":
                    expanded_group.append((kind, token))
        if expanded_group:
            expanded.append(expanded_group)
    return expanded


def make_grouped_sql_clause(expanded, column, db):
    clauses = ""
    esc = escape_sql_string
    first_group = True
    for group in expanded:
        clause = ""
        neg = False
        has_null = False
        first_token, first_value = group[0]
        if first_token == "NOT":
            neg = True
            if len(group) > 1:
                second_token, second_value = group[1]
                if second_token == "RANGE":
                    lower, upper = second_value.split("-")
                    clause += "(%s < %s OR %s > %s)" % (column, esc(lower), column, esc(upper))
                    if first_group:
                        first_group = False
                        clauses += clause
                    else:
                        clauses += "AND %s" % clause
                    continue
            clause += "%s NOT IN (" % column
        else:
            if first_token == "RANGE":
                lower, upper = first_value.split("-")
                if not lower:
                    c = db.dbh.cursor()
                    c.execute("select min(%s) from toms" % column)
                    lower = str(c.fetchone()[0])
                if not upper:
                    c = db.dbh.cursor()
                    c.execute("select max(%s) from toms" % column)
                    upper = str(c.fetchone()[0])
                clause += "(%s >= %s AND %s <= %s)" % (column, esc(lower), column, esc(upper))
                if first_group:
                    first_group = False
                    clauses += clause
                else:
                    try:
                        clauses += "AND %s" % clause
                    except UnicodeDecodeError:
                        clauses += "AND %s" % clause
                continue
            clause += "%s IN (" % column
        # if we don't have a range, we have something that we can evaluate
        # as an exact IN/NOT IN expression
        first_value = True
        for kind, token in group:
            if kind == "OR" or kind == "NOT":
                continue
            if kind == "NULL":
                #                clause += "NULL"
                has_null = True  # this is a hack--NULL is both in the IN clause, where it is ineffectual
                continue
            if first_value:
                first_value = False
            else:
                clause += ", "
            if kind == "QUOTE":
                try:
                    clause += esc(token[1:-1])
                except:
                    clause += esc(token[1:-1])
                # but harmless, as well was its own clause below.  Fix later, if possible.
        clause += ")"
        if has_null:
            if not neg:
                clause += "OR %s IS NULL" % column
            else:
                clause += "AND %s IS NOT NULL" % column
        if first_group:
            first_group = False
            clauses += "(%s)" % clause
        else:
            clauses += " AND (%s)" % clause
    return "(%s)" % clauses


def metadata_pattern_search(term, path):
    command = ["egrep", "-awie", "[[:blank:]]?%s" % term, "%s" % path]
    grep = subprocess.Popen(command, stdout=subprocess.PIPE, env=os.environ)
    cut = subprocess.Popen(["cut", "-f", "2"], stdin=grep.stdout, stdout=subprocess.PIPE)
    match, stderr = cut.communicate()
    matches = [i for i in match.decode("utf8", "ignore").split("\n") if i]
    return matches


def escape_sql_string(s):
    s = s.replace("'", "''")
    return "'%s'" % s


def hit_to_string(hit, width):
    if isinstance(hit, sqlite3.Row):
        hit = hit["philo_id"]
    if isinstance(hit, str):
        hit = [int(x) for x in hit.split(" ")]
    if isinstance(hit, int):
        hit = [hit]
    if len(hit) > width:
        hit = hit[:width]
    pad = width - len(hit)
    hit_string = " ".join(str(h) for h in hit)
    hit_string += "".join(" 0" for n in range(pad))
    return hit_string


def str_to_hit(string):
    return [int(x) for x in string.split(" ")]


def obj_cmp(x, y):
    for a, b in zip(x, y):
        if a < b:
            return -1
        if a > b:
            return 1
    else:
        return 0


def corpus_cmp(x, y):
    if 0 in x:
        depth = x.index(0)
    else:
        depth = len(x)
    return obj_cmp(x[:depth], y[:depth])
