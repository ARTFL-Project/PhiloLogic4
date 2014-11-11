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
            }
        }
    });
    
    $('#nav-buttons').on('affix.bs.affix', function() {
        $(this).addClass('fixed');
        adjustTocHeight();
        $("#toc-container").css({'position': 'fixed', "top": "32px"}); // Force position fixed because of bottom event hack
        $('#back-to-top').velocity('fadeIn', {duration: 200});
    });
    $('#nav-buttons').on('affix-top.bs.affix', function() {
        $(this).removeClass('fixed');
        adjustTocHeight();
        $('#back-to-top').velocity('fadeOut', {duration: 200});
        $("#toc-container").css({'position': 'static', "top": "auto"}); // Force position static because of bottom event hack
    });
    
    $('#back-to-top').click(function() {
        $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
    })
    
    // Handle page reload properly
    var db_url = webConfig['db_url'];
    if ($('#book-page').length) {
        backForwardButtonReload(db_url);
    }
    
    // Note handling
    createNoteLink();
    
    // Only enable back/forward buttons if necessary 
    checkEndBeginningOfDoc();
    
    $(window).load(function() {
        if ($('.highlight').length) {
            scrollToHighlight();
        }
        retrieveTableOfContents(db_url);
        retrieveObj(db_url);
    });
    
    // Make sure notes stay inline when after a span.xml-l
    $('.xml-l + .note').prev('.xml-l').css('display', 'inline');
    $('.note-content + .xml-l').prepend('<br>');
    
});


////////////////////////////////////////////////////////////////////////////////
//////////// FUNCTIONS /////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////


function createNoteLink() {
    $('.note-content').each(function() {
        $(this).before('<a class="note" tabindex="0" data-toggle="popover" data-container="body" data-placement="right" data-trigger="focus">note</a>');
    }).promise().done(function() {
        $('.note').popover({animate: true, trigger: 'focus', html: true, content: function() {
            return $(this).next('.note-content').html();
        }});
    });
}

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

// Check to see if the footer is no longer at the bottomw of the page
function checkFooterPosition() {
    
}

function retrieveTableOfContents(db_url) {
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var my_path = pathname.replace(/\/\d+.*$/, '/');
    var doc_id = pathname.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
    var philo_id = doc_id + ' 0 0 0 0 0 0'
    var script = $('#toc-wrapper').data('script') + philo_id;
    $('#toc-container').hide();
    $.getJSON(script, function(data_object) {
        var html = '';
        var data = data_object.toc;
        for (var i=0; i < data.length; i++) {
            var philo_id = data[i].philo_id.split(' ').join('_');
            var philo_type = data[i].philo_type;
            var head = data[i].display_name;
            var href = data[i].link;
            var link = '<a href="'+ href + '" id="' + philo_id + '">' + head + '</a>';
            if (philo_type == "div2") {
                html += '<div class="toc-div2"><span class="bullet-point-div2"></span>' + link + '</div>';
            } else if (philo_type == "div3") {
                html += '<div class="toc-div3"><span class="bullet-point-div3"></span>' + link + '</div>';
            } else {
                html += '<div class="toc-div1"><span class="bullet-point-div1"></span>' + link + '</div>';
            }
        }
        $('#toc-content').html(html).promise().done(function() {
            $("#show-toc").removeAttr("disabled");
        });
        adjustTocHeight(100); // adjust height before showing
        TocLinkHandler(db_url);
    });
}

function hideTOC() {
    $('#toc-container').velocity("transition.slideLeftBigOut", {"duration": 300});
    $("#toc-container").data("status", "closed");
    setTimeout(function() {
        if ($(document).height() == $(window).height()) {
            $('#toc-container').css('position', 'static');
        }
    });
    $('#nav-buttons').removeClass('col-md-offset-4');
}

function showTOC() {
    if ($(document).height() == $(window).height()) {
        $('#toc-container').css('position', 'static');
    }
    $("#toc-container").data("status", "open");
    $('#toc-wrapper').css('opacity', 1);
    $('#nav-buttons').addClass('col-md-offset-4');
    $('#toc-container').velocity("transition.slideLeftBigIn", {"duration": 300});
    $('#toc-wrapper').addClass('show');
    var scrollto_id = '#' + $("#text-obj-content").data('philoId').split(' ').join('_');
    setTimeout(function() {
        adjustTocHeight();
        if ($('#toc-content').find($(scrollto_id)).length) {
            $('#toc-content').scrollTo($(scrollto_id), 500);
            $('#toc-content').find($(scrollto_id)).addClass('current-obj');
        }  
    }, 300);
}

function adjustTocHeight(num) {
    // Make sure the TOC is no higher than viewport
    if ($(document).height() == $(window).height()) {
        var toc_height = $('#footer').offset().top - $('#nav-buttons').position().top - $('#nav-buttons').height() - $('#toc-titlebar').height() - 40;
    } else {
        var toc_height = $(window).height() - $("#footer").height() - $('#nav-buttons').position().top - $('#toc-titlebar').height() - 50;
    }
    if (typeof num !="undefined") {
        toc_height = toc_height - num;
    }
    $('#toc-content').velocity({'max-height': toc_height + 'px'});
}

function scrollToHighlight() {
    var word_offset = $('.highlight').eq(0).offset().top;
    if (word_offset == 0) {
        var note = $('.highlight').parents('.note-content');
        note.show(); // The highlight is in a hidden note
        word_offset = $('.highlight').offset().top;
        $('.highlight').parents('.note-content').hide();
    }
    if ($('.highlight').eq(0).parents('.note-content').length) {
        $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: word_offset - 60, complete: function() {
            $('.highlight').parents('.note-content').prev('.note').trigger('focus');}}
        );
    } else {
        $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: word_offset - 40});
    }
    
}

/// Go to next or previous object in text display
function retrieveObj(db_url){
    $("#prev-obj, #next-obj").on('click', function() {
        var my_path = db_url.replace(/\/\d+.*$/, '/');
        var philo_id = $(this).data('philoId');
        var script = $('#all-content').data('script') + philo_id;
        var width = $(window).width() / 2 - 100;
        $("#waiting").css("margin-left", width).css('margin-top', $(window).scrollTop() + 250).css({"display": "block", "opacity": 1});
        $('#waiting').velocity({rotateZ: 7200}, {duration: 20000, easing: "linear"});
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
        var script = $('#all-content').data('script') + philo_id;
        var width = $(window).width() / 2 - 100;
        $("#waiting").css("margin-left", width).css('margin-top', $(window).scrollTop() + 250).css({"display": "block", "opacity": 1});
        $('#waiting').velocity({rotateZ: 7200}, {duration: 20000, easing: "linear"});
        $.getJSON(script, function(data) {
            newTextObjectCallback(data, philo_id, my_path);
        });
    });
}

// Callback function after a new text object has been retrieved
function newTextObjectCallback(data, philo_id, my_path) {
    $("#waiting").velocity('fadeOut', {duration: 100, queue:false, complete:function() {
        $(this).velocity("reverse", {duration:100})}});
    var scrollto_id = '#' + $("#text-obj-content").data('philoId').split(' ').join('_');
    $('#toc-content').find($(scrollto_id)).removeClass('current-obj');
    $('#text-obj-content').fadeOut('fast', function() {
        $(this).replaceHtml(data['text']).fadeIn('fast');
        $('#text-obj-content').data("philoId", philo_id);
        $('#prev-obj').data('philoId', data['prev']);
        $('#next-obj').data('philoId', data["next"]);
        var scrollto_id = '#' + $("#text-obj-content").data('philoId').split(' ').join('_');
        if ($('#toc-content').find($(scrollto_id)).length) {
            $('#toc-content').scrollTo($(scrollto_id), 500);
            $('#toc-content').find($(scrollto_id)).addClass('current-obj');
        }
        var new_url = my_path + '/dispatcher.py/' + philo_id.split(' ').join('/');
        History.pushState(null, '', new_url);
        checkEndBeginningOfDoc();
        if ($('body').scrollTop() != 0) {
            $('body').velocity('scroll', {duration: 200, offset: 0, easing: 'easeOut', complete: function() {$('#toc-container').css('position', 'static');}});
        }
        adjustTocHeight();
        createNoteLink();
        setTimeout(function() {
            $('#toc-container').css('position', 'static')
        }, 250);
        addPreviousPage();
    });
}