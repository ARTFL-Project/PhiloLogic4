var latestKnownScrollY = 0;
var window_height = $(window).height();
var toc_open = false;

$(document).ready(function() {
    
    // jQueryUI theming
    $('#show_table_of_contents, #prev_obj, #next_obj').button();
    
    $(window).resize(function() {
        window_height = $(window).height();
    });
    //
    // This is to display the table of contents in the document viewer
    var db_url = webConfig['db_url'];
    if ($('#next_obj').length) {
        back_forward_button_reload(db_url);
    }
    
    page_image_link();
    
    var text = 'Click to see a full-sized version of this image';
    $('.plate_img').attr('title', text).tooltip({ position: { my: "left center", at: "right center" } });
    
    var toc = $('#prev_and_toc');
    var prev = $('#prev_obj');
    var next = $('#next_and_read');
    var top = next.offset().top - parseFloat(next.css('marginTop').replace(/auto/, 0));
    $(window).scroll(function() {
        latestKnownScrollY = window.pageYOffset;
        follow_scroll(toc, prev, next, top);
    });
    
    checkEndBeginningOfDoc();
    
    $(window).load(function() {
        if ($('.highlight').length) {
            scrollToHighlight();
        }
        t_o_c_handler(db_url);
        retrieveObj(db_url);
    });
    
});


////////////////////////////////////////////////////////////////////////////////
//////////// FUNCTIONS /////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

function checkEndBeginningOfDoc() {
    if ($('#next_obj').data('philoId') == "") {
        $('#next_obj_wrapper').hide();
    } else {
        $('#next_obj_wrapper').show();
    }
    if ($("#prev_obj").data('philoId') == "") {
        $("#prev_obj").hide();
    } else {
        $("#prev_obj").show();
    }
}

function follow_scroll(toc, prev, next, top) {
    if (latestKnownScrollY >= top) {
        next.css('position', 'fixed');
        toc.css({'position': 'fixed', 'top': 0});
        prev.css({'position': 'fixed', 'top': 0});
    } else {
        // otherwise remove it
        next.css('position', 'static');
        toc.css({'position': 'static', 'top': ''});
        prev.css({'position': 'absolute', 'top': ''});
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
    var max_height = maxPossibleHeight - footer_offset - 30;
    $('#toc_container').css('max-height', max_height);
}

function scrollToHighlight() {
    var word_offset = $('.highlight').offset().top - 40;
    $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: word_offset});
}


/// Go to next or previous object in text display
function retrieveObj(db_url){
    $("#prev_obj, #next_obj").on('click', function() {
        var my_path = db_url.replace(/\/\d+.*$/, '/');
        var philo_id = $(this).data('philoId');
        var script = my_path + '/scripts/go_to_obj.py?philo_id=' + philo_id;
        var width = $(window).width() / 2 - 100;
        $("#waiting").css("margin-left", width).css('margin-top', $(window).scrollTop() + 150).show();
        $.getJSON(script, function(data) {
            $("#waiting").fadeOut('fast');
            var scrollto_id = '#' + $("#obj_text").data('philoId').replace(/ /g, '_');
            $('#toc_container').find($(scrollto_id)).attr('style', 'color: #990000;');
            $('#obj_text').fadeOut('fast', function() {
                $(this).html(data['text']).fadeIn('fast');
                $('#footer').css('top', '');
                $('#obj_text').data("philoId", philo_id);
                $('#prev_obj').data('philoId', data['prev']);
                $('#next_obj').data('philoId', data["next"]);
                var scrollto_id = '#' + $("#obj_text").data('philoId').replace(/ /g, '_');
                if ($('#toc_container').find($(scrollto_id)).length) {
                    $('#toc_container').scrollTo($(scrollto_id), 500);
                    $('#toc_container').find($(scrollto_id)).attr('style', 'color: black; font-weight: 700 !important;');
                }
                page_image_link();
                var new_url = my_path + '/dispatcher.py/' + philo_id.replace(/ /g, '/');
                History.pushState(null, '', new_url);
                checkEndBeginningOfDoc();
            });
        });
    });
}

function back_forward_button_reload(db_url) {
    $(window).on('popstate', function() {
        var id_to_load = window.location.pathname.replace(/.*dispatcher.py\//, '').replace(/\//g, ' ');
        id_to_load = id_to_load.replace(/( 0 ?)*$/g, '');
        if (id_to_load != $('#obj_text').data('philoId').replace(/( 0)*$/g, '')) {
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
    var my_path = pathname.replace(/\/\d+.*$/, '/');
    var doc_id = pathname.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
    var philo_id = doc_id + ' 0 0 0 0 0 0'
    var script = my_path + '/scripts/get_table_of_contents.py?philo_id=' + philo_id;
    $('#t_b_c_box').attr('style', 'color: LightGray;');
    $.get(script, function(data) {
        $('#toc_container').html(data);
        $('#t_b_c_box').animate({color: '#555 !important'},400, function() {
            $("#show_table_of_contents").click(function() {
                toc_height();
                toc_open = true;
                show_hide_toc(text_position);
                TocLinkHandler(db_url);
            });
        });
    });
}


function show_hide_toc(top_right) {
    var position = top_right - ($('#toc_container').width() - $('.table_of_contents').width()) - 15;
    if ($("#t_b_c_box").text() == "Table of contents") {
        $("#t_b_c_box").html("Hide table of contents");
        $('#toc_container').addClass('show');
        setTimeout(function() {
            var scrollto_id = '#' + $("#obj_text").data('philoId').replace(/ /g, '_');
            $('#toc_container').scrollTo($(scrollto_id), 500);
            $('#toc_container').find($(scrollto_id)).css('color', 'black');
            $(scrollto_id).delay(500).animate({backgroundColor: '#ffdb9e'}, 300).animate({backgroundColor: '#FAFAFA'}, 300);
        }, 400);
    } else {
        $('#toc_container').removeClass('show');
        $('#show_table_of_contents').button('refresh');
        setTimeout(function() {     // Avoid weird effect on toc_container
            $("#t_b_c_box").html("Table of contents");
        }, 100);
    }
}

function TocLinkHandler(db_url) {
    $('#table_of_contents a').click(function(e) {
        e.preventDefault();
        var my_path = db_url.replace(/\/\d+.*$/, '/');
        var philo_id = $(this).attr('id').replace(/_/g, ' ');
        var script = my_path + '/scripts/go_to_obj.py?philo_id=' + philo_id;
        var width = $(window).width() / 2 - 100;
        $("#waiting").css("margin-left", width).css('margin-top', $(window).scrollTop() + 150).show();
        $.getJSON(script, function(data) {
            var scrollto_id = '#' + $("#obj_text").data('philoId').replace(/ /g, '_');
            $('#toc_container').find($(scrollto_id)).attr('style', 'color: #990000;');
            $("#waiting").fadeOut('fast');
            $('#obj_text').fadeOut('fast', function() {
                $(this).html(data['text']).fadeIn('fast');
                $('#footer').css('top', '');
                $('#obj_text').data("philoId", philo_id);
                $('#prev_obj').data('philoId', data['prev']);
                $('#next_obj').data('philoId', data["next"]);
                var scrollto_id = '#' + $("#obj_text").data('philoId').replace(/ /g, '_');
                if ($('#toc_container').find($(scrollto_id)).length) {
                    $('#toc_container').scrollTo($(scrollto_id), 500);
                    $('#toc_container').find($(scrollto_id)).attr('style', 'color: black; font-weight: 700 !important;');
                }
                page_image_link();
                var new_url = my_path + '/dispatcher.py/' + philo_id.replace(/ /g, '/');
                History.pushState(null, '', new_url);
                checkEndBeginningOfDoc();
            });
        });
        
    })
}

// Encyclopedie functions
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
