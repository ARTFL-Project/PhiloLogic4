"use strict";

var window_height = $(window).height();

$(document).ready(function() {
    
    $("#show-toc").click(function() {
        if ($("#toc-container").data("status") == "closed") {
            showTOC();
        } else {
            hideTOC();
        }
    });
    $("#hide-toc").click(function() {
        hideTOC()
    });
    
    // Previous and next button follow scroll
    $('#nav-buttons, #toc-container').affix({
        offset: {
        top: function() {
            return (this.top = $('#nav-buttons').offset().top)
            },
        bottom: function() {
            return (this.bottom = $('#footer').outerHeight(true))
          }
        }
    });
    
    $('#nav-buttons').on('affix.bs.affix', function() {
        $(this).addClass('fixed');
        adjustTocHeight();
        $("#toc-container").css({'position': 'fixed'}); // Force position fixed because of bottom event hack
        $('#back-to-top').velocity('fadeIn', {duration: 200});
    });
    $('#nav-buttons').on('affix-top.bs.affix', function() {
        $(this).removeClass('fixed');
        adjustTocHeight();
        $('#back-to-top').velocity('fadeOut', {duration: 200});
        $("#toc-container").css({'position': 'static'}); // Force position static because of bottom event hack
    });
    $('#toc-container').on('affixed-bottom.bs.affix', function() {
        adjustTocHeight(50);
        $(this).css({'position': 'fixed'}); // Force position fixed in order to override the position relative set on this event
    });
    
    $('#back-to-top').click(function() {
        $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
    })
    
    // Handle page reload properly
    var db_url = webConfig['db_url'];
    if ($('#book-page').length) {
        backForwardButtonReload(db_url);
    }
    
    page_image_link();
    
    var text = 'Click to see a full-sized version of this image';
    $('.plate_img').attr('title', text).tooltip({ position: { my: "left center", at: "right center" } });
    
    // Only enable back/forward buttons if necessary 
    checkEndBeginningOfDoc();
    
    $(window).load(function() {
        if ($('.highlight').length) {
            scrollToHighlight();
        }
        retrieveTableOfContents(db_url);
        retrieveObj(db_url);
    });
    
});


////////////////////////////////////////////////////////////////////////////////
//////////// FUNCTIONS /////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

function checkEndBeginningOfDoc() {
    if ($('#next-obj').data('philoId') == "") {
        $('#next-obj').attr('disabled', 'disabled');
    } else {
        $('#next-obj').removeAttr('disabled');
    }
    if ($("#prev-obj").data('philoId') == "") {
        $("#prev-obj").attr('disabled', 'disabled');
    } else {
        $("#prev-obj").removeAttr('disabled');
    }
}

function retrieveTableOfContents(db_url) {
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var my_path = pathname.replace(/\/\d+.*$/, '/');
    var doc_id = pathname.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
    var philo_id = doc_id + ' 0 0 0 0 0 0'
    var script = my_path + '/scripts/get_table_of_contents.py?philo_id=' + philo_id;
    $("#show-toc").removeAttr("disabled");
    $('#toc-container').hide();
    $.get(script, function(data) {
        $('#toc-content').html(data);
        // Add a negative left margin to hide on the left side
        var tocWidth = $('#toc-wrapper').outerWidth() + 30; // account for container margin
        $('#toc-container').css('margin-left', '-' + tocWidth + 'px').css('display', 'inline-block');
        adjustTocHeight(100); // adjust height before showing
        TocLinkHandler(db_url);
    });
}

function hideTOC() {
    if ($(document).height() == $(window).height()) {
        $('#toc-container').css('position', 'static');
    }
    $("#toc-container").data("status", "closed");
    var tocWidth = $('#toc-container').outerWidth() + 30; // account for container margin
    $('#toc-container').velocity({'margin-left': '-' + tocWidth + 'px'}, {"duration": 300});
    $('#nav-buttons').removeClass('col-md-offset-4');
}
function showTOC() {
    if ($(document).height() == $(window).height()) {
        $('#toc-container').css('position', 'static');
    }
    $("#toc-container").data("status", "open");
    adjustTocHeight();
    $('#toc-wrapper').css('opacity', 1);
    $('#nav-buttons').addClass('col-md-offset-4');
    $('#toc-container').velocity({'margin-left': '0px'}, {"duration": 300});
    $('#toc-wrapper').addClass('show');
    var scrollto_id = '#' + $("#text-obj-content").data('philoId').replace(/ /g, '_');
    setTimeout(function() {
        if ($('#toc-content').find($(scrollto_id)).length) {
            $('#toc-content').scrollTo($(scrollto_id), 500);
            $('#toc-content').find($(scrollto_id)).addClass('current-obj');
        }  
    }, 300);
}
function adjustTocHeight(num) {
    // Make sure the TOC is no higher than viewport
    if ($(document).height() == $(window).height()) {
        var toc_height = $('#footer').offset().top - $('#nav-buttons').position().top - $('#nav-buttons').height() - $('#toc-titlebar').height() - 30;
    } else {
        var toc_height = $(window).height() - $("#footer").height() - $('#nav-buttons').position().top - $('#toc-titlebar').height() - 40;
    }
    if (typeof num !="undefined") {
        toc_height = toc_height - num;
    }
    $('#toc-content').velocity({'height': toc_height + 'px'});
}

function scrollToHighlight() {
    var word_offset = $('.highlight').offset().top - 40;
    $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: word_offset});
}

/// Go to next or previous object in text display
function retrieveObj(db_url){
    $("#prev-obj, #next-obj").on('click', function() {
        var my_path = db_url.replace(/\/\d+.*$/, '/');
        var philo_id = $(this).data('philoId');
        var script = my_path + '/scripts/go_to_obj.py?philo_id=' + philo_id;
        var width = $(window).width() / 2 - 100;
        $("#waiting").css("margin-left", width).css('margin-top', $(window).scrollTop() + 150).show();
        $.getJSON(script, function(data) {
            newTextObjectCallback(data, philo_id, my_path);
        });
    });
}

function backForwardButtonReload(db_url) {
    $(window).on('popstate', function() {
        var id_to_load = window.location.pathname.replace(/.*dispatcher.py\//, '').replace(/\//g, ' ');
        id_to_load = id_to_load.replace(/( 0 ?)*$/g, '');
        if (id_to_load != $('#text-obj-content').data('philoId').replace(/( 0)*$/g, '')) {
            window.location = window.location.href;
        }
    });
}

function TocLinkHandler(db_url) {
    $('#toc-content a').click(function(e) {
        e.preventDefault();
        var my_path = db_url.replace(/\/\d+.*$/, '/');
        var philo_id = $(this).attr('id').replace(/_/g, ' ');
        var script = my_path + '/scripts/go_to_obj.py?philo_id=' + philo_id;
        var width = $(window).width() / 2 - 100;
        $("#waiting").css("margin-left", width).css('margin-top', $(window).scrollTop() + 150).show();
        $.getJSON(script, function(data) {
            newTextObjectCallback(data, philo_id, my_path);
        });
    });
}

// Callback function after a new text object has been retrieved
function newTextObjectCallback(data, philo_id, my_path) {
    $("#waiting").fadeOut('fast');
    var scrollto_id = '#' + $("#text-obj-content").data('philoId').replace(/ /g, '_');
    $('#toc-content').find($(scrollto_id)).removeClass('current-obj');
    $('#text-obj-content').fadeOut('fast', function() {
        $(this).replaceHtml(data['text']).fadeIn('fast');
        $('#text-obj-content').data("philoId", philo_id);
        $('#prev-obj').data('philoId', data['prev']);
        $('#next-obj').data('philoId', data["next"]);
        var scrollto_id = '#' + $("#text-obj-content").data('philoId').replace(/ /g, '_');
        if ($('#toc-content').find($(scrollto_id)).length) {
            $('#toc-content').scrollTo($(scrollto_id), 500);
            $('#toc-content').find($(scrollto_id)).addClass('current-obj');
        }
        page_image_link();
        var new_url = my_path + '/dispatcher.py/' + philo_id.replace(/ /g, '/');
        History.pushState(null, '', new_url);
        checkEndBeginningOfDoc();
        $('body').velocity('scroll', {duration: 200, offset: 0, easing: 'easeOut'});
    });
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