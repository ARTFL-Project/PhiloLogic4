$(document).ready(function() {
    
    var page_pos = $('.book_page').offset().left;
    $('.book_page').css('margin-left', page_pos);
    left_pos();
    right_pos();

    // Change pages
    $(".fake_prev_page, .fake_next_page").on('click', function() {
        var direction = $(this).attr('class');
        var page_count = $(".obj_text").children('div').size();
        var visible = $(".obj_text").children("div:visible")
        if (direction == "fake_prev_page") {
            $(".obj_text").children().filter("div:visible").hide().prev().fadeIn('fast');
        } else {
            $(".obj_text").children().filter("div:visible").hide().next().fadeIn('fast');
        }
    });
    
    // This is to display the table of contents in the document viewer
    var db_url = db_locals['db_url'];
    if ($('.next_obj').length) {
        retrieve_obj(db_url);
        t_o_c_handler(db_url);
        follow_scroll($('.prev_and_toc'), $('.next_and_read'));
        if ($('.highlight').length) {
            $(window).load(function() {
                scroll_to_highlight();
            });
        }
        back_forward_button_reload(db_url);
    } else if ($('.next_page').length) {
        retrieve_page(db_url);
        t_o_c_handler(db_url);
        follow_scroll($('.prev_and_toc'), $('.next_and_read'));
        if ($('.highlight').length) {
            $(window).load(function() {
                scroll_to_highlight();
            });
        }
    }
    
    display_overlay();
    page_image_link();
    
});


////////////////////////////////////////////////////////////////////////////////
//////////// FUNCTIONS /////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////


function right_pos() {
    var right_pos = $('.book_page').offset().left + $('.book_page').width();
    $('.next_obj_wrapper').css('margin-left', right_pos + 33);
}
function left_pos() {
    var prev_obj_pos = $('.prev_obj').offset().left + $('.prev_obj').width();
    var page_pos = $('.book_page').offset().left;
    var distance = page_pos - prev_obj_pos;
    $('#prev_and_toc_button').css('margin-left', distance - 40);
}

function scroll_to_highlight() {
    var word_offset = $('.highlight').offset().top - 40;
    $("html, body").animate({ scrollTop: word_offset }, 'slow');
}

function page_image_link() {
    $('.page_image_link').click(function(e) {
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

// Display overlay to enable a reading mode //
function display_overlay() {
    $("#overlay_toggler").click(function() {
        if ($("#overlay").is('*')) {
            $(".book_page").css('box-shadow', '0px 0px 15px #888888');
            $("#overlay").fadeOut('fast', function() {
                $(this).remove();
                $("#read").html('Start reading mode').fadeIn('fast');
            });
        } else {
            var docHeight = $(document).height();
            $("body").append("<div id='overlay' style='display:none;'></div>");
            $(".book_page").css('position', 'relative').css('box-shadow', '0px 0px 15px #FFFFFF');
            $("#read").html('Exit reading mode').fadeIn('fast');
            $(".read_button, .next_obj").css('z-index', 100).css('position', 'relative');
            $('.next_and_read').css('z-index', 100);
            $('.initial_form').css('z-index', 98);
            $('.book_page').css('z-index', 100);
            $("#overlay")
               .height(docHeight)
               .css({
                  'opacity' : 0.7,
                  'position': 'absolute',
                  'top': 0,
                  'left': 0,
                  'background-color': 'black',
                  'width': '100%',
                  'z-index': 99
                });
            $("#overlay").fadeIn('fast');
        }
    });
}

/// Go to next or previous object in text display
function retrieve_obj(db_url){
    $(".prev_obj, .next_obj").on('click', function() {
        var my_path = db_url.replace(/\/\d+.*$/, '/');
        var philo_id = $(this).attr('id');
        var script = my_path + '/scripts/go_to_obj.py?philo_id=' + philo_id;
        $.getJSON(script, function(data) {
            var scrollto_id = '#' + $(".obj_text").attr('id');
            $('#toc_container').find($(scrollto_id)).attr('style', 'color: #800000;');
            $('.obj_text').fadeOut('fast', function() {
                $(this).html(data['text']).fadeIn('fast');
                $('#footer').css('top', '');
                $('.obj_text').attr("id", philo_id.replace(/ /g, '_'));
                $('.prev_obj').attr('id', data['prev']);
                $('.next_obj').attr('id', data["next"]);
                $("html, body").animate({ scrollTop: 0 }, "fast");
                var scrollto_id = '#' + $(".obj_text").attr('id');
                if ($('#toc_container').find($(scrollto_id)).length) {
                    $('#toc_container').scrollTo($(scrollto_id), 500);
                    $('#toc_container').find($(scrollto_id)).attr('style', 'color: black; font-weight: 700 !important;');
                }
                page_image_link();
                var new_url = my_path + '/dispatcher.py/' + philo_id.replace(/ /g, '/');
                History.pushState(null, '', new_url);
            });
        });
    });
}
function retrieve_page(db_url) {
    $(".prev_page, .next_page").on('click', function() {
        var my_path = db_url.replace(/(\/\d+)+$/, '/');
        var doc_id = db_url.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
        var page = $(".book_page").attr('id');
        var go_to_page = $(this).attr('id');
        var myscript = my_path + "/scripts/go_to_page.py?philo_id=" + doc_id + "&go_to_page=" + go_to_page + "&doc_page=" + page;
        $.getJSON(myscript, function(data) {
            $(".book_page").attr('id', data[2]);
            $('.obj_text').fadeOut('fast', function () {
                $(this).html(data[3]).fadeIn('fast');
                $('#footer').css('top', '');
                $(".prev_page").attr("id", data[0]);
                $('.next_page').attr('id', data[1]);
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
        id_to_load = id_to_load.replace(/(_0)*$/g, '');
        if (id_to_load != $('.obj_text').attr('id').replace(/(_0)*$/g, '')) {
            window.location = window.location.href;
        }
    });
}

/// Have previous and next links follow scroll in page and object navigation ///
function t_o_c_handler(db_url) {
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var text_position = $('.book_page').offset().left + 20;
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
                show_hide_toc(text_position);
            });
        });
    });
}
function follow_scroll(prev, next) {
    var top = next.offset().top - parseFloat(next.css('marginTop').replace(/auto/, 0));
    $(window).scroll(function (event) {
      // what the y position of the scroll is
        var y = $(this).scrollTop();
      
        // whether that's below the form
        if (y >= top) {
            // if so, ad the fixed class
            next.addClass('fixed');
            prev.addClass('fixed');
        } else {
            // otherwise remove it
            prev.removeClass('fixed');
            next.removeClass('fixed');
        }
        var position = $('#toc_container').offset().top;
        var toc_header_height = $(".prev_and_toc").height() + parseInt($(".prev_and_toc").css("margin-top")) + parseInt($("#toc_container").css("margin-top"));
        var other_content = $(".prev_obj_wrapper").position().top - window.pageYOffset;
        if (other_content > 0) { toc_header_height += other_content; }
        var maxPossibleHeight = $(window).height() - toc_header_height;
        var bottomPosition = $(window).height() + window.pageYOffset;
        var footer_pos = $("#footer").offset().top;        
        var footer_offset = 0;
        if (bottomPosition > footer_pos) {
            footer_offset = bottomPosition - footer_pos;            
        }
        var max_height = maxPossibleHeight - footer_offset;
        $('#toc_container').css('max-height', max_height);
    });
}
function show_hide_toc(top_right) {
    var position = top_right - ($('#toc_container').width() - $('.table_of_contents').width()) - 15;
    var scrollto_id = '#' + $(".obj_text").attr('id');
    if ($("#t_b_c_box").text() == "Show table of contents") {
        $("#t_b_c_box").html("Hide table of contents");
        $('#toc_container').animate({
            'margin-left': '-30px'
            }, 450
            );
        $('#toc_container').scrollTo($(scrollto_id), 500);
        $('#toc_container').find($(scrollto_id)).attr('style', 'color: black;');
    } else {
        $("#t_b_c_box").html("Show table of contents");
        $('#toc_container').animate({
                'margin-left': '-700px'
        }, 450);
        $('#show_table_of_contents').button('refresh');
    }
}