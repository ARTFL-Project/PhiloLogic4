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
        <div class="object_display">
        <a class="fake_prev_page"><</a>
        <a class="fake_next_page">></a>
        <div class="obj_text">
        ${obj_text}
        </div>
        </div>
  </div>
<%include file="footer.mako"/>