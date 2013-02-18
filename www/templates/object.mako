<%include file="header.mako"/>
  <div class='philologic_response'>
    <div class='philologic_cite'>
        <span class='title'>${obj.author}, <i>${obj.title}</i> Tome ${obj.volume}</span>
    </div>
        <div>
        ${navigate_obj(obj, query_args=q['byte'])}
        </div>
        <div class='more'>
        % if obj.prev:
            <% 
            prev_id = obj.prev.split(" ")[:7]
            prev_url = f.link.make_absolute_object_link(db,prev_id)
            %>
            <a href='${prev_url}' class='previous'>Previous</a>
        % endif
        % if obj.next:
            <%
            next_id = obj.next.split(" ")[:7]
            next_url = f.link.make_absolute_object_link(db,next_id)
            %>
            <a href='${next_url}' class='next'>Next</a>
        % endif
        <div style='clear:both;'></div>
  </div>
<%include file="footer.mako"/>