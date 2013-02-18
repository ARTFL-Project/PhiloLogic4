<%include file="header.mako"/>
  <div class='philologic_response'>
    <div class='philologic_cite'>
        <span class='title'>${obj.author}, <i>${obj.title}</i> Tome ${obj.volume}</span>
    </div>
    <% results = navigate_doc(obj, db) %>
    % for i in results:
        <% 
        id = i.philo_id[:7]
        href = f.link.make_absolute_object_link(db,id)
        if i.type == "div2":
            spacing = "&nbsp;-&nbsp;"
        elif i.type == "div3":
            spacing = "&nbsp;&nbsp;&nbsp;-&nbsp;"       
        else:
            spacing = ""
        %>
        ${spacing}<a href="${href}">${i.head or "[%s]" % i.type}</a><br>
    % endfor
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
