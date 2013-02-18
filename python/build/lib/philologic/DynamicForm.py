import re
def validate(form):
    r = {}
    q = form.getfirst("query")
    if q:
        r["query"] = q
    else:
        r["query"] = ""

    r["meta"] = []
    i = 1
    while True:
        meta_n = "meta" + str(i)
        m_dict = {}
        if meta_n in form:
            m_dict["value"] = form[meta_n].value
        if meta_n + "field" in form:
            m_dict["field"] = form[meta_n + "field"].value
        if meta_n + "type" in form:
            m_dict["type"] = form[meta_n + "type"].value
        if meta_n + "op" in form:
            m_dict["op"] = form[meta_n + "op"].value
        if m_dict == {}:
            break
        r["meta"].append(m_dict)
        i += 1
    return r

def generate(df,dbname):
    r = ""
    r += '<form action="%s">\n' % ("/cgi-bin/pyphilo/cgi4.py/" + dbname)
    r += '<table style="border:none">\n'
    r += '<tr><td>query:</td><td><input name="query" type="text" value="%s"/></td></tr>' % df["query"]
    i = 1
    if df["meta"] == []:
        df["meta"] = [{"value":""}]
    for m in df["meta"]:
        this = "meta" + str(i)
        next = "meta" + str(i + 1)
        r += '<tr>\n'
        r += '<td>meta:</td><td><input name="%s" type="text" value="%s"/>' % (this,m["value"] if "value" in m else "")
        r += ' in <select name="%s"><option value="">any</option>\n' % (this + "field")

        for fieldname in ["author","title","head","filename"]:
            sel = ""
            if "field" in m and m["field"] == fieldname: 
                sel = "selected='selected'"
            r += '<option value="%s" %s>%s</option>\n' % (fieldname,sel,fieldname)
        r += "</select>"
        r += '<select name="%s"><option value="">object</option>\n' % (this + "type")
        for object in ["doc","div","div1","div2","div3"]:
            sel = ""
            if "type" in m and m["type"] == object:
                sel = "selected='selected'"
            r += '<option value="%s" %s>%s</option>\n' % (object,sel,object)
        r += "</select>"
        i += 1
        r += '<select name=%s><option value="" selected="selected">.</option> \
                              <option value="and">and</option> \
                              <option value="or">or</option></select>' % (next + "op")
    r += "</td></tr></table><input type='submit'/></form>"
    return r

def formmatch(df,object):
    r = False
    for m in df["meta"]:
        if "op" not in m or m["op"] == "or":
            if r == True:
                break
            else:
                r = metamatch(m,object)
        elif m["op"] == "and":
            r = r and metamatch(m,object)
    return r

def metamatch(meta,object):
    if "value" not in meta:
        return True
    if meta.get("type"):
        if object["type"] != meta["type"]:
            return False
    if meta.get("field"):
        if meta["field"] not in object:
            return False
        elif re.search(meta["value"],object[meta["field"]],re.IGNORECASE):
            return True
    else:
        for field in object:
            if field != "id":
                if re.search(meta["value"],object[field],re.IGNORECASE):
                    return True
    return False

def getjs():
    r = """
    <script type="text/javascript" src="/jquery-1.4.2.min.js"></script>
    <script type="text/javascript">
    $(document).ready(function(){
        $("select[name*=op]").change(function() {
            1;
        });
    });
    
    </script>
    """
    return r