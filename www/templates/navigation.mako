<%include file="header.mako"/>
  <div class='philologic_response'>
    <div class='philologic_cite'>
        <div class='title'>${obj.author}, <i>${obj.title}</i> Tome ${obj.volume}</div>
    </div>
    <div id="table_toggler" class="table_toggler">
    <input type="checkbox" id="show_table_of_contents">
    <label for="show_table_of_contents"><span id="t_b_c_box">Show table of contents</span></label>
    </div>
    <% results = navigate_doc(obj, db) %>
    <div id="table_of_contents" class="table_of_contents">
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
    </div>
    <div class='page_display'>
    <p class="page_number">
    <a href="?&doc_page=${prev_page}" class="prev_next"><</a>
    ${current_page}
    <a href="?&doc_page=${next_page}" class="prev_next">></a>
    </p>
    ${page_text}
    </div>
        <div style='clear:both;'>
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
