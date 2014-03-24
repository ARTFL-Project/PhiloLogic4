<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div id='philologic_response'>
    <div id='object_title'>
        <span class='philologic_cite'>${f.cite.make_abs_doc_cite(db,obj)}</span>
    </div>
    <div id="page_display">
        <div id="prev_obj_wrapper">
            <div id= "prev_and_toc">
                <div id='prev_and_toc_button'>
                    <div id='show_table_of_contents'>
                        <label for="show_table_of_contents"><span id="t_b_c_box">Table of contents</span></label>
                    </div>
                </div>
                <div id="table_toggler">
                    <div id="toc_container"></div>
                </div>
            </div>
        </div>
        <div id="prev_obj" data-philo-id="${prev}">&lt;</div>
        <div id="next_obj_wrapper">
            <div id ="next_and_read">
                <span id="next_obj" data-philo-id="${next}">&gt;</span>
            </div>
        </div>
        <div id="book_page">
            <div id="obj_text" data-philo-id="${'_'.join([str(j) for j in obj.philo_id])}">${obj_text}</div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>