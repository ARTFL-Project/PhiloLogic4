$(document).ready(function() {
    
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = webConfig['db_url'];
    var q_string = window.location.search.substr(1);
    concordance_kwic_switch(db_url);
    back_forward_button_concordance_reload();
    if ($('#kwic_concordance').length) {
        var config = {    
                over: showBiblio, 
                timeout: 50,  
                out: hideBiblio   
            };
        $(".kwic_biblio").hoverIntent(config);
    }
    
    $(window).load(function() {
         // Get the total results when available
        if ($('#incomplete').text() != '.') {
            $.getJSON($("#search-hits").data('script'), function(data) {
                $('#total_results, #incomplete').fadeOut('fast', function() {
                    if (parseInt($('#end').text()) > data) {
                        $('#end').text(data);
                    }
                    $("#total_results").text(data);
                    $('#incomplete').text('.')
                }).fadeIn('fast');
            });
        }
    });
    
    // Fetch more context for concordances after page load
    $(window).load(function() {
        fetchMoreContext();
    });
    
});

/// Switch betwwen concordance and KWIC reports
function concordance_kwic_switch(db_url) {
    $("#report_switch button").on('click touchstart', function(e) {
        e.stopPropagation();
        var script = $(this).data('script');
        var switchto = $(this).data('report');
        var width = $(window).width() / 2 - 100;
        $("#waiting").css({"margin-left": width, "margin-top": 320, "opacity": 1}).show();
        $('#waiting').velocity({rotateZ: 3600}, {duration: 10000, easing: "linear"});
        $.get(script, function(html_results) {
            $("#report_switch button").toggleClass('active');
            $("#waiting").velocity("stop").velocity('fadeOut', {duration: 200, queue:false, complete:function() {
                $(this).velocity("reverse", {duration:100})}});
            $("#results_container").hide().html(html_results).velocity('fadeIn', {duration: 200});
            if (switchto == "kwic") {
                var config = {    
                    over: showBiblio, 
                    timeout: 100,  
                    out: hideBiblio   
                };
                $(".kwic_biblio").hoverIntent(config);
                $('#concordance').removeAttr("checked").parent().removeClass('active');
                $('#kwic').prop("checked", true).parent().addClass('active');
                var new_url = History.getState().url.replace(/report=concordance/, 'report=kwic');
                History.pushState(null, '', new_url);
            } else {
                $('#kwic').removeAttr("checked").parent().removeClass('active');
                $('#concordance').prop("checked", true).parent().addClass('active');
                var new_url = History.getState().url.replace(/report=kwic/, 'report=concordance');
                History.pushState(null, '', new_url);
            }
            fetchMoreContext();
            $('.more a').each(function() {
                if (switchto == "kwic") {
                    var new_href = $(this).attr('href').replace('concordance', 'kwic');
                }
                else {
                    var new_href = $(this).attr('href').replace('kwic', 'concordance');
                }
                $(this).attr('href', new_href);
            });
        });
    });
}

function back_forward_button_concordance_reload() {
    $(window).on('popstate', function() {
        var report = window.location.href.replace(/.*?report=([^\W]+).*/, '$1');
        // Concordance is the default report if no report is specified
        if (report.match(/kwic|concordance/) === null) {
            report = "concordance";
        }
        if (report != $("#report_switch .active").data('report')) {
            window.location = window.location.href;
        }
    });
}

// These functions are for the kwic bibliography which is shortened by default
function showBiblio() {
    $(this).children(".full_biblio").addClass('show');
}

function hideBiblio() {
    $(this).children(".full_biblio").velocity('fadeOut', {duration: 200, complete:function() {$(this).removeClass('show')}});
}

