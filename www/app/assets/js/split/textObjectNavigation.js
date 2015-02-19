"use strict";

var window_height = $(window).height();

$(document).ready(function() {
    
});


////////////////////////////////////////////////////////////////////////////////
//////////// FUNCTIONS /////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////


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