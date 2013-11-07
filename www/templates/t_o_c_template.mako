<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<div id='philologic_response'>
    <div class='t_o_c_title'>
        <span class='philologic_cite'>${f.cite.make_abs_doc_cite(db,obj)}</span>
    </div>
    <%include file="toc.mako"/>
</div>
<%include file="footer.mako"/>