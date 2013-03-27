from wsgiref.handlers import CGIHandler
from wsgiref.util import shift_path_info
from wsgiref.util import request_uri

metadata = ["author","title","date"]

def form_service(environ,start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'text/html;charset=UTF-8')] # HTTP Headers
    start_response(status, headers)
    yield "<html><body>"
    yield "<form class='philologic_search_form' action='.'>"
    yield "<table class='table_form'>"
    yield "<tr><td>query:</td><td><input type='text' name='query'/></td></tr>\n"
    yield "<tr><td colspan='2'><select name='query_method'>"
    yield "<option value='phrase'>exactly</option>"
    yield "<option value='proxy' selected='true'>within</option>"
    yield "</select>"
    yield "<input type='text' size='1'name='query_arg' value='1'/> word(s) </td></tr>"
    for field in metadata:
        yield "<tr><td>%s:</td><td><input type='text' name='%s'/></td></tr>\n" % (field,field)

    yield "<tr><td colspan='2'>group by: <select name='field'>"
    yield "<option value='title' > title</option>\n"
    yield "<option value='date' selected='true'> date</option>\n"
    yield "<option value='author'> author</option>\n"
    yield "<option value='collocates'> collocates</option>\n"
    yield "</select></td></tr>\n"
    yield "<tr><td colspan='2'><input type='submit'/></td></tr>\n"
    yield "</table>"
    yield "</form>"
    yield "</body></html>"
