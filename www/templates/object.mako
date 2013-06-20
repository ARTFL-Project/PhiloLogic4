<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script>
$(document).ready(function() {
    var page_pos = $('.book_page').offset().left;
    $('.book_page').css('margin-left', page_pos);
    left_pos();
    right_pos();
});
function right_pos() {
    var right_pos = $('.book_page').offset().left + $('.book_page').width();
    $('.next_obj_wrapper').css('margin-left', right_pos + 33);
}
function left_pos() {
    var prev_obj_pos = $('.prev_obj').offset().left + $('.prev_obj').width();
    var page_pos = $('.book_page').offset().left;
    var distance = page_pos - prev_obj_pos;
    console.log(prev_obj_pos, page_pos, distance)
    $('#prev_and_toc_button').css('margin-left', distance - 40);
}
</script>
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