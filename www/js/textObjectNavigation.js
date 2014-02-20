var latestKnownScrollY = 0;
var window_height = $(window).height();
var toc_open = false;

$(document).ready(function() {
    
    // jQueryUI theming
    $('#show_table_of_contents').button();
    
    adjustPageWidth(),
    $(window).resize(function() {
        adjustPageWidth();
        window_height = $(window).height();
    })

    // Change pages
    $("#fake_prev_page, #fake_next_page").on('click', function() {
        var direction = $(this).attr('class');
        var page_count = $("#obj_text").children('div').size();
        var visible = $("#obj_text").children("div:visible")
        if (direction == "fake_prev_page") {
            $("#obj_text").children().filter("div:visible").hide().prev().fadeIn('fast');
        } else {
            $("#obj_text").children().filter("div:visible").hide().next().fadeIn('fast');
        }
    });
    
    // This is to display the table of contents in the document viewer
    var db_url = db_locals['db_url'];
    if ($('#next_obj').length) {
        retrieve_obj(db_url);
        back_forward_button_reload(db_url);
    }
    
    page_image_link();
    
    var text = 'Click to see a full-sized version of this image';
    $('.plate_img').attr('title', text).tooltip({ position: { my: "left center", at: "right center" } });
    
    var prev = $('#prev_and_toc');
    var next = $('#next_and_read');
    var top = next.offset().top - parseFloat(next.css('marginTop').replace(/auto/, 0));
    $(window).scroll(function() {
        latestKnownScrollY = window.pageYOffset;
        follow_scroll(prev, next, top);
    });
    
    checkEndOfDoc();
    
    $(window).load(function() {
        if ($('.highlight').length) {
            scroll_to_highlight();
        }
        t_o_c_handler(db_url);
    });
    
});


////////////////////////////////////////////////////////////////////////////////
//////////// FUNCTIONS /////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

function adjustPageWidth() {
    var window_width = $(window).width();
    if (window_width < 1204) {
        var right_margin = parseInt($("#book_page").css('margin-right')) - (1204 - window_width);
        var adjusted_width = $("#book_page").width() - (window_width - 1204);
        if (right_margin < 80) {
            adjusted_width = 'auto';
            right_margin = 80;
        }
        $('#book_page').css({'margin-left': '200px', 'margin-right': right_margin, 'width': adjusted_width});
    } else {
        var adjusted_width = window_width - 500;
        if (adjusted_width > 700) {
            adjusted_width = 700;  
        }
        $("#book_page").css({'margin': '0 auto', 'width': adjusted_width});
    }
    positionPrevNext();
    $('#toc_container').css('width', $('#book_page').css('margin-left'));
}

function positionPrevNext() {
    var page_pos = $('#book_page').offset().left - 25;
    left_pos(page_pos);
    right_pos();
}

function checkEndOfDoc() {
    if ($('#next_obj').data('philoId') == "") {
        $('#next_obj_wrapper').hide();
    } else {
        $('#next_obj_wrapper').show();
    }
}

function follow_scroll(prev, next, top) {
    if (latestKnownScrollY >= top) {
        next.css('position', 'fixed');
        prev.css({'position': 'fixed', 'top': 0});
    } else {
        // otherwise remove it
        next.css('position', 'static');
        prev.css({'position': 'static', 'top': ''});
    }
    if (toc_open) {
        toc_height();
    }
}

function toc_height() {
    var position = $('#toc_container').offset().top;
    var toc_header_height = $("#prev_and_toc").height() + parseInt($("#prev_and_toc").css("margin-top")) + parseInt($("#toc_container").css("margin-top"));
    var other_content = $("#prev_obj_wrapper").position().top - latestKnownScrollY;
    if (other_content > 0) { toc_header_height += other_content; }
    var maxPossibleHeight = window_height - toc_header_height;
    var bottomPosition = window_height + latestKnownScrollY;
    var footer_pos = $("#footer").offset().top;        
    var footer_offset = 0;
    if (bottomPosition > footer_pos) {
        footer_offset = bottomPosition - footer_pos + 22;            
    }
    var max_height = maxPossibleHeight - footer_offset;
    $('#toc_container').css('max-height', max_height);
}


function right_pos() {
    var right_pos = $('#book_page').offset().left + $('#book_page').width();
    $('#next_obj_wrapper').css('margin-left', right_pos + 30);
}
function left_pos(page_pos) {
    var prev_obj_width = $('#prev_obj').width();
    var distance = page_pos - 60;
    $('#prev_obj').css('margin-left', distance);
}

function scroll_to_highlight() {
    var word_offset = $('.highlight').offset().top - 40;
    $("html, body").animate({ scrollTop: word_offset }, 'slow', 'easeOutCirc');
}

function page_image_link() {
    $('#page_image_link, .plate_img_link').click(function(e) {
        e.preventDefault();
        var href = $(this).attr('href');
        var image = $("<img />").attr('src', href).load(function() {
            var div = '<div class="image_container" style="display: none;"></div>'
            $('.page_display').prepend(div);
            var close_div = '<div id="close_page_image" class="ui-icon ui-icon-circle-close close_page_image"></div>'
            $('.image_container').append(close_div)
            $("body").append("<div id='overlay' style='display:none;'></div>");
            var header_height = $('#header').height();
            var footer_height = $('#footer').height();
            var overlay_height = $(document).height() - header_height - footer_height;
            $("#overlay")
            .height(overlay_height)
            .css({
               'opacity' : 0.3,
               'position': 'absolute',
               'top': 0,
               'left': 0,
               'background-color': 'white',
               'width': '100%',
               'margin-top': header_height,
               'z-index': 90
             });
            $("html, body").animate({ scrollTop: 140 }, "slow");
            $('.image_container').append(image);
            $('.image_container, #overlay').fadeIn('fast');
            var image_height = $('.image_container').offset().top + $('.image_container').height();
            image_height = image_height + parseInt($('.image_container').css('border-top-width')) + parseInt($('.image_container').css('border-bottom-width'));
            var original_footer_offset = $('#footer').offset().top;
            if (image_height > $('#footer').offset().top) {
                $('#footer').offset({top: image_height});
            }
            $("#close_page_image, #overlay").click(function() {
                $('.image_container, #overlay').fadeOut('fast', function() {
                    $('#overlay').remove();
                    $('.image_container').remove();
                    if ($('#footer').offset().top > original_footer_offset) {
                        $("html, body").animate({ scrollTop: 0 }, function() {
                            $('#footer').animate({top: original_footer_offset});
                        });
                    }
                });
            });
        });
    });
}

function plate_hover() {
    $('.plate_img_link').hover(function() {
        var text = 'Click to see a full-sized version of this image';
        $(this).tooltip({content: text});
    });
}



/// Go to next or previous object in text display
function retrieve_obj(db_url){
    $("#prev_obj, #next_obj").on('click', function() {
        var my_path = db_url.replace(/\/\d+.*$/, '/');
        var philo_id = $(this).data('philoId');
        var script = my_path + '/scripts/go_to_obj.py?philo_id=' + philo_id;
        $.getJSON(script, function(data) {
            var scrollto_id = '#' + $("#obj_text").data('philoId');
            $('#toc_container').find($(scrollto_id)).attr('style', 'color: #990000;');
            $('#obj_text').fadeOut('fast', function() {
                $(this).html(data['text']).fadeIn('fast');
                $('#footer').css('top', '');
                $('#obj_text').data("philoId", philo_id.replace(/ /g, '_'));
                $('#prev_obj').data('philoId', data['prev']);
                $('#next_obj').data('philoId', data["next"]);
                $("html, body").animate({ scrollTop: 0 }, "fast");
                var scrollto_id = '#' + $("#obj_text").data('philoId');
                if ($('#toc_container').find($(scrollto_id)).length) {
                    $('#toc_container').scrollTo($(scrollto_id), 500);
                    $('#toc_container').find($(scrollto_id)).attr('style', 'color: black; font-weight: 700 !important;');
                }
                page_image_link();
                var new_url = my_path + '/dispatcher.py/' + philo_id.replace(/ /g, '/');
                History.pushState(null, '', new_url);
                checkEndOfDoc();
            });
        });
    });
}
function retrieve_page(db_url) {
    $("#prev_page, #next_page").on('click', function() {
        var my_path = db_url.replace(/(\/\d+)+$/, '/');
        var doc_id = db_url.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
        var page = $("#book_page").attr('id');
        var go_to_page = $(this).attr('id');
        var myscript = my_path + "/scripts/go_to_page.py?philo_id=" + doc_id + "&go_to_page=" + go_to_page + "&doc_page=" + page;
        $.getJSON(myscript, function(data) {
            $("#book_page").attr('id', data[2]);
            $('#obj_text').fadeOut('fast', function () {
                $(this).html(data[3]).fadeIn('fast');
                $('#footer').css('top', '');
                $("#prev_page").attr("id", data[0]);
                $('#next_page').attr('id', data[1]);
                page_image_link();
                var new_url = my_path + '/dispatcher.py/' + philo_id.replace(/ /g, '/');
                History.pushState(null, '', new_url);
            }); 
        });
        
    });
}
function back_forward_button_reload(db_url) {
    $(window).on('popstate', function() {
        var id_to_load = window.location.pathname.replace(/.*dispatcher.py\//, '').replace(/\//g, '_');
        id_to_load = id_to_load.replace(/(_0_?)*$/g, '');
        if (id_to_load != $('#obj_text').data('philoId').replace(/(_0)*$/g, '')) {
            window.location = window.location.href;
        }
    });
}

/// Have previous and next links follow scroll in page and object navigation ///
function t_o_c_handler(db_url) {
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var text_position = $('#book_page').offset().left - 20;
    var position = $('#toc_container').offset().top;
    var bottomPosition = $(window).height();
    var footer_pos = $("#footer").offset().top - 30;
    if (bottomPosition < footer_pos) {
        var max_height = bottomPosition - position;
    } else {
        var max_height = footer_pos - position;
    }
    $('#toc_container').css('max-height', max_height);
    $('#toc_container').css('width', text_position);
    var my_path = pathname.replace(/\/\d+.*$/, '/');
    var doc_id = pathname.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
    var philo_id = doc_id + ' 0 0 0 0 0 0'
    var script = my_path + '/scripts/get_table_of_contents.py?philo_id=' + philo_id;
    $('#t_b_c_box').attr('style', 'color: LightGray;');
    $.get(script, function(data) {
        $('#toc_container').css('position', 'absolute');
        $('#toc_container').hide().css('margin-left', '-700px').html(data).show();
        $('#t_b_c_box').animate({color: '#555 !important'},400, function() {
            $("#show_table_of_contents").click(function() {
                toc_height();
                toc_open = true;
                show_hide_toc(text_position);
            });
        });
    });
}

function show_hide_toc(top_right) {
    var position = top_right - ($('#toc_container').width() - $('.table_of_contents').width()) - 15;
    var scrollto_id = '#' + $("#obj_text").data('philoId');
    if ($("#t_b_c_box").text() == "Table of contents") {
        $("#t_b_c_box").html("Hide table of contents");
        $('#toc_container').animate({
            'margin-left': '-30px'
            }, 450
            );
        $('#toc_container').scrollTo($(scrollto_id), 500);
        $('#toc_container').find($(scrollto_id)).css('color', 'black');
        $(scrollto_id).delay(500).animate({backgroundColor: '#ffdb9e'}, 300).animate({backgroundColor: ''}, 300);
    } else {
        $("#t_b_c_box").html("Table of contents");
        $('#toc_container').animate({
                'margin-left': '-700px'
        }, 450);
        $('#show_table_of_contents').button('refresh');
    }
}