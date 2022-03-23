import os
import sqlite3
import struct
import subprocess
import sys
import unicodedata

from . import HitList
from .HitList import NoHits
from .QuerySyntax import group_terms, parse_query, parse_date_query

os.environ["PATH"] += ":/usr/local/bin/"


def metadata_query(db, filename, param_dicts, sort_order, raw_results=False, ascii_sort=True):
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
    return HitList.HitList(filename, 0, db, raw=raw_results, sort_order=sort_order, ascii_sort=ascii_sort)


def metadata_total_word_count_query(db, metadata, metadata_field_name):
    """Retrieve word count from text object"""
    param_dicts = [{} for level in db.locals["metadata_hierarchy"]]
    # Taken from DB.query
    for k, v in list(metadata.items()):
        for i, params in enumerate(db.locals["metadata_hierarchy"]):
            if v and (k in params):
                param_dicts[i][k] = v
                if k in db.locals["metadata_types"]:
                    this_type = db.locals["metadata_types"][k]
                    if this_type == "div":
                        param_dicts[i]["philo_type"] = ['"div"|"div1"|"div2"|"div3"']
                    else:
                        param_dicts[i]["philo_type"] = ['"%s"' % db.locals["metadata_types"][k]]
    param_dicts = [d for d in param_dicts if d]
    if "philo_id" in metadata:
        if param_dicts:
            param_dicts[-1]["philo_id"] = metadata["philo_id"]
        else:
            param_dicts.append({"philo_id": metadata["philo_id"]})
    prev = None
    query = None
    for param_dict in param_dicts:
        query = query_recursive(db, param_dict, prev, None)
        prev = query
    cursor = db.dbh.cursor()
    philo_type = db.locals["metadata_types"][metadata_field_name]
    if query is not None:
        philo_ids = []
        for row in query:
            philo_ids.append(row["philo_id"])
        if philo_type != "div":
            cursor.execute(
                f"SELECT {metadata_field_name}, SUM(word_count) AS total_sum FROM toms WHERE philo_id IN ({', '.join('?' for _ in range(len(philo_ids)))}) AND philo_type='{philo_type}' GROUP BY {metadata_field_name}",
                tuple(philo_ids),
            )
        else:
            cursor.execute(
                f"SELECT {metadata_field_name}, SUM(word_count) AS total_sum FROM toms WHERE philo_id IN ({', '.join('?' for _ in range(len(philo_ids)))}) AND philo_type IN ('div1', 'div2', 'div3') GROUP BY {metadata_field_name}",
                tuple(philo_ids),
            )
    else:
        if philo_type != "div":
            cursor.execute(
                f"SELECT {metadata_field_name}, SUM(word_count) AS total_sum FROM toms WHERE philo_type='{philo_type}' GROUP BY {metadata_field_name}"
            )
        else:
            cursor.execute(
                f"SELECT {metadata_field_name}, SUM(word_count) AS total_sum FROM toms WHERE philo_type IN ('div1', 'div2', 'div3') GROUP BY {metadata_field_name}"
            )
    results = {row[metadata_field_name]: row["total_sum"] for row in cursor}
    return results


def query_recursive(db, param_dict, parent, sort_order):
    """Build recursise SQL query"""
    r = query_lowlevel(db, param_dict, sort_order)
    if parent:
        try:
            outer_hit = next(parent)
        except StopIteration:
            return
        for inner_hit in r:
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
    """SQL query builder"""
    vars = []
    clauses = []
    for column, values in list(param_dict.items()):
        norm_path = db.path + "/frequencies/normalized_" + column + "_frequencies"
        for v in values:
            parsed = "text"
            if db.locals.metadata_sql_types[column] in ("text", "int"):
                parsed = parse_query(v)
            elif db.locals.metadata_sql_types[column] == "date":
                v = v.replace('"', "")  # remove quotes
                parsed = parse_date_query(v)
            grouped = group_terms(parsed)
            expanded = expand_grouped_query(grouped, norm_path)
            sql_clause = make_grouped_sql_clause(expanded, column, db)
            if db.locals["debug"]:
                print("METADATA_TOKENS:", parsed, file=sys.stderr)
                print("METADATA_SYNTAX GROUPED:", grouped, file=sys.stderr)
                print("METADATA_SYNTAX EXPANDED:", expanded, file=sys.stderr)
                print("SQL_SYNTAX:", sql_clause, file=sys.stderr)
            clauses.append(sql_clause)
    if not sort_order:
        sort_order = ["rowid"]
    if clauses:
        query = "SELECT philo_id FROM toms WHERE " + " AND ".join("(%s)" % c for c in clauses)
    else:
        query = "SELECT philo_id FROM toms"
    if sort_order:
        query = f"{query} ORDER BY {', '.join(sort_order)}"
    if db.locals["debug"]:
        print("INNER QUERY: ", "%s %% %s" % (query, vars), sort_order, file=sys.stderr, flush=True)
    results = db.dbh.execute(query, vars)
    return results


def expand_grouped_query(grouped, norm_path):
    """Expand grouped SQL query"""
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
    """Make SQL clauses"""
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
                if second_token in ("RANGE", "DATE_RANGE"):
                    if first_token == "RANGE":
                        lower, upper = second_value.split("-")
                    else:
                        lower, upper = second_value.split("<=>")
                    clause += f"({column} < {esc(lower)} OR {column} > {esc(upper)})"
                    if first_group:
                        first_group = False
                        clauses += clause
                    else:
                        clauses += f"AND {clause}"
                    continue
            clause += f"{column} NOT IN ("
        else:
            if first_token in ("RANGE", "DATE_RANGE"):
                if first_token == "RANGE":
                    lower, upper = first_value.split("-")
                else:
                    lower, upper = first_value.split("<=>")
                if not lower:
                    c = db.dbh.cursor()
                    c.execute(f"select min({column}) from toms")
                    lower = str(c.fetchone()[0])
                if not upper:
                    c = db.dbh.cursor()
                    c.execute("select max({column}) from toms")
                    upper = str(c.fetchone()[0])
                clause += f"({column} >= {esc(lower)} AND {column} <= {esc(upper)})"
                if first_group:
                    first_group = False
                    clauses += clause
                else:
                    clauses += f"AND {clause}"
                continue
            clause += f"{column} IN ("
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
                clause += esc(token[1:-1])
                # but harmless, as well was its own clause below.  Fix later, if possible.
            if kind == "DATE":
                clause += esc(token)
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
    """Create egrep pattern to find metadata"""
    command = ["egrep", "-awie", "[[:blank:]]?%s" % term, "%s" % path]
    grep = subprocess.Popen(command, stdout=subprocess.PIPE, env=os.environ)
    cut = subprocess.Popen(["cut", "-f", "2"], stdin=grep.stdout, stdout=subprocess.PIPE)
    match, _ = cut.communicate()
    matches = [i for i in match.decode("utf8", "ignore").split("\n") if i]
    return matches


def escape_sql_string(s):
    """Escape SQL string"""
    s = s.replace("'", "''")
    return "'%s'" % s


def hit_to_string(hit, width):
    """Convert Philo hit to a string"""
    if isinstance(hit, sqlite3.Row):
        hit = hit["philo_id"]
    if isinstance(hit, str):
        hit = list(map(int, hit.split(" ")))
    if isinstance(hit, int):
        hit = [hit]
    if len(hit) > width:
        hit = hit[:width]
    pad = width - len(hit)
    hit_string = " ".join(map(str, hit))
    hit_string += "".join(" 0" for _ in range(pad))
    return hit_string


def str_to_hit(string):
    """Convert string to hit"""
    return list(map(int, string.split(" ")))


def obj_cmp(x, y):
    """Compare function"""
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
