$(document).ready(function() {
    
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = webConfig['db_url'];
    var q_string = window.location.search.substr(1);
    concordance_kwic_switch(db_url);
    back_forward_button_concordance_reload();
    
    if (global_report == "kwic") {
        var config = {over: showBiblio, 
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
        if (global_report == "concordance") {
            fetchMoreContext();
        }
    });
    
    $('#page-links a').on('click touchstart', function(e) {
        e.preventDefault();
        $('#current_results_page').removeClass('active').removeAttr('id');
        $(this).attr('id', 'current_results_page').addClass('active');
        var script = $(this).data('script');
        $.getJSON(script, function(data) {
            concordanceRenderer(data);
            var new_url = script.replace('format=json', 'format=');
            History.pushState(null, '', new_url);
        });
    });
    
});

/// Concordance template
function concordanceRenderer(data) {
    var html = '<ol id="philologic_concordance">';
    var results = data.results;
    for (var i=0; i < results.length; i++) {
        var result = results[i];
        var n = data.description.start + i;
        html += '<li class="philologic_occurrence panel panel-default">';
        html += '<div class="citation-container row">';
        html += '<div class="col-xs-12 col-sm-10 col-md-11">';
        var philo_id = result.philo_id.join(' ');
        html += '<span class="cite" data-id="' + philo_id + '">';
        html += n + '.&nbsp ' + result.citation;
        html += '</span></div>';
        html += '<div class="hidden-xs col-sm-2 col-md-1">';
        html += '<button class="btn btn-primary more_context pull-right" disabled="disabled" data-context="short">More</button>';
        html += '</div></div>';
        html += '<div class="philologic_context">';
        html += '<div class="default_length">' + result.context + '</div>';
        html += '</div></li>';
    }
    html += '</ol>';
    $('#results_container').hide().empty();
    $('#results_container').append(html).velocity('fadeIn');
    
}

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
                fetchMoreContext();
            }
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

