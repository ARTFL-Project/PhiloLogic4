$(document).ready(function() {
    
    // jQueryUI theming
    $("#report_switch").buttonset();
    $('#page_links').find('a').each(function(){$(this).button()});
    
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = db_locals['db_url'];
    var q_string = window.location.search.substr(1);
    concordance_kwic_switch(db_url);
    back_forward_button_concordance_reload();
    more_context();
    sidebar_reports(q_string, db_url, pathname);
    if ($('.kwic_concordance').length) {
        var config = {    
                over: showBiblio, 
                timeout: 100,  
                out: hideBiblio   
            };
        $(".kwic_biblio").hoverIntent(config);
    }
    
    getCitationWidth();
    $(window).resize(function() {
        getCitationWidth();
    });
    $(window).load(function() {
         // Get the total results when available
        if ($('#incomplete').text() != '.') {
            $.getJSON(db_url + '/scripts/get_total_results.py?' + q_string, function(data) {
                $('#total_results, #incomplete').fadeOut('fast', function() {
                    $("#total_results").text(data);
                    $('#incomplete').text('.')
                }).fadeIn('fast');
            });
        }
    });
    
});



/// Switch betwwen concordance and KWIC reports
function concordance_kwic_switch(db_url) {
    $("#report_switch").on("change", function() {
        $('.highlight_options').remove();
        var switchto = $('input[name=report_switch]:checked').val();
        var width = $(window).width() / 3;
        $("#waiting").css("margin-left", width).show();
        $("#waiting").css("margin-top", 200).show();
        $.get(db_url + "/reports/concordance_switcher.py" + switchto, function(data) {
            $("#results_container").hide().empty().html(data).fadeIn('fast');
            $("#waiting").hide();
            if (switchto.match(/kwic/)) {
                var config = {    
                    over: showBiblio, 
                    timeout: 100,  
                    out: hideBiblio   
                };
                $(".kwic_biblio").hoverIntent(config);
                $('#concordance').removeAttr("checked");
                $('#kwic').prop("checked", true)
                var new_url = History.getState().url.replace(/report=concordance/, 'report=kwic');
                History.pushState(null, '', new_url);
            }
            else {
                $('#kwic').removeAttr("checked");
                $('#concordance').prop("checked", true);
                var new_url = History.getState().url.replace(/report=kwic/, 'report=concordance');
                History.pushState(null, '', new_url);
            }
            $("#report").buttonset("refresh");
            display_options_on_selected();
            more_context();
            getCitationWidth();
            $('.more').find('a').each(function() {
                if (switchto.match(/kwic/)) {
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
        if ($('#concordance_switch').prop('checked')) {
            var report_displayed = "concordance";
        } else {
            var report_displayed = 'kwic'
        }
        if (report != report_displayed) {
            window.location = window.location.href;
        }
    });
}

// These functions are for the kwic bibliography which is shortened by default
function showBiblio() {
    $(this).children("#full_biblio").css('position', 'absolute').css('text-decoration', 'underline')
    $(this).children("#full_biblio").css('background', 'LightGray')
    $(this).children("#full_biblio").css('box-shadow', '5px 5px 15px #C0C0C0')
    $(this).children("#full_biblio").css('display', 'inline')
}

function hideBiblio() {
    $(this).children("#full_biblio").fadeOut(200)
}

