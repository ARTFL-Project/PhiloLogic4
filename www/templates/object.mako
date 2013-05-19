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
    <div style="float:right;" id="overlay_toggler"><label for="overlay_toggler">
        <span id="read">Start reading mode</span></label>
    </div>
   
    <div class="page_display">
        <div class="book_page">
            <div class="next_obj_wrapper">
                <div class="next_obj" id="${next}">&gt;</div>
            </div>
            <div class="prev_obj_wrapper">
                <div class="prev_obj" id="${prev}">&lt;</div>
            </div>
            <div class="obj_text">${obj_text}</div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>