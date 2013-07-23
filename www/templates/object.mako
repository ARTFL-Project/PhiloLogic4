<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script type="text/javascript" src="${db.locals['db_url']}/js/textObjectNavigation.js"></script>
<div class='philologic_response'>
    <div class='object_title'>
        <span class='philologic_cite'>${f.cite.make_abs_doc_cite(db,obj)} <b>Volume ${obj.volume}</b></span>
    </div>
    <div class="page_display">
        <div class="prev_obj_wrapper">
            <div class='prev_and_toc'>
                <div id='prev_and_toc_button'>
                    <div class='t_o_c_button'>
                        <input type="checkbox" id="show_table_of_contents">
                        <label for="show_table_of_contents"><span id="t_b_c_box">Show table of contents</span></label>
                    </div>
                    <div class="prev_obj" id="${prev}">&lt;</div>
                </div>
                <div id="table_toggler" class="table_toggler">
                    <div id="toc_container" style='float:left;'></div>
                </div>
            </div>
        </div>
        <div class="next_obj_wrapper">
            <div class='next_and_read'>
                <span class="next_obj" id="${next}">&gt;</span>
                <div class='read_button'>
                    <span id="overlay_toggler"><label for="overlay_toggler">
                    <span id="read">Start reading mode</span></label>
                    </span>
                </div>
            </div>
        </div>
        <div class="book_page">
            <div class="obj_text" id="${'_'.join([str(j) for j in obj.philo_id])}">${obj_text}</div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>