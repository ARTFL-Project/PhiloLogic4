from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
from wsgiref.util import request_uri
import philologic.PhiloDB
import urlparse

metadata = ["author","title","date"]

def form_service(environ,start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'text/html; charset=UTF-8')] # HTTP Headers
    start_response(status, headers)
    environ["parsed_params"] = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    # a wsgi app is supposed to return an iterable;
    # yielding lets you stream, rather than generate everything at once.
    if "philologic_dbname" in environ:
        dbname = environ["philologic_dbname"]
    else:
        dbname = environ["parsed_params"]["philologic_dbname"][0]
    db = philologic.PhiloDB.PhiloDB("/var/lib/philologic/databases/"+dbname)

    yield "<html><body>"
    yield "<form class='philologic_search_form' action='.'>"
    yield "<table class='table_form'>"
    yield "<tr><td>query:</td><td><input type='text' name='query'/></td></tr>\n"
    yield "<tr><td colspan='2'><select name='query_method'>"
    yield "<option value='phrase'>exactly</option>"
    yield "<option value='proxy' selected='true'>within</option>"
    yield "</select>"
    yield "<input type='text' size='1'name='query_arg' value='1'/> word(s) </td></tr>"
    for field in db.locals["metadata_fields"]:
        yield "<tr><td>%s:</td><td><input type='text' name='%s'/></td></tr>\n" % (field,field)

    printedfirst = False
    yield "<tr><td colspan='2'>group by: <select name='field'>"
    for field in db.locals["metadata_fields"] + ["collocates"]: 
        yield "<option value='%s' > %s </option>" % (field,field)
    yield "</select></td></tr>\n"
    yield "<tr><td colspan='2'><input type='submit'/></td></tr>\n"
    yield "</table>"
    yield "</form>"
    yield "</body></html>"
