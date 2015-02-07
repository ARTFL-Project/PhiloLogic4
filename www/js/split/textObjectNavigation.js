"use strict";

var window_height = $(window).height();

$(document).ready(function() {
    
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
    
});


////////////////////////////////////////////////////////////////////////////////
//////////// FUNCTIONS /////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////


function createNoteLink() {
    $('.note-ref, .note').click(function() {
        if ($(this).hasClass == ".note") {
            $(this).popover({animate: true, trigger: 'focus', html: true, content: function() {
                return $(this).next('.note-content').html();
            }});
        } else {
            var link = $(this).data('ref');
            var element = $(this);
            //element.popover({trigger: 'manual'});
            $.getJSON(link, function(data) {
                element.popover({trigger: 'manual', content: function() {
                    return data.text;
                }});
                if (data.text != '') {
                    element.popover("show");
                } else {
                    alert('PhiloLogic was unable to retrieve a note at the given link')
                }
                $('body').on('click', function (e) {
                    //did not click a popover toggle, or icon in popover toggle, or popover
                    if ($(e.target).data('toggle') !== 'popover') { 
                        element.popover('hide');
                    }
                });
            });
        }
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
        var script = $('#all-content').data('script') + '&philo_id=' + philo_id;
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
        var script = $('#all-content').data('script') + '&philo_id=' + philo_id;
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
    });
}