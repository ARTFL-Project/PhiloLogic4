<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<div class='philologic_response'>
    <div class='philologic_cite'>
        <div class='title'>${obj.author}, <i>${obj.title}</i> Tome ${obj.volume}</div>
    </div>
    <div id="table_toggler" class="table_toggler">
        <input type="checkbox" id="show_table_of_contents">
        <label for="show_table_of_contents"><span id="t_b_c_box">Show table of contents</span></label>
    </div>
    <div style="float:right;" id="overlay_toggler"><label for="overlay_toggler"><span id="read">Start reading mode</span></label></div>
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
        <div class="book_page">
            <a id="${prev_page}" class="prev_page"><</a>
            <a id="${next_page}" class="next_page">></a>   
            <div id="current_page" class="current_page">${current_page}</div>
            <div class="page_text" id="page_text">${page_text}</div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>
