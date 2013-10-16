$(document).ready(function() {
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
    
    closeConcordance();
    $('.close_concordance').hide();
    
    getCitationWidth()
    $(window).resize(function() {
        getCitationWidth();
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
            $('.close_concordance').button();
            closeConcordance();
            $('.close_concordance').hide();
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

//    These functions are for the sidebar frequencies
function sidebar_reports(q_string, db_url, pathname) {
    $("#toggle_frequency").click(function() {
        toggle_frequency(q_string, db_url, pathname);
    });
    $("#frequency_field").change(function() {
        toggle_frequency(q_string, db_url, pathname);
    });
    $(".hide_frequency").click(function() {
        hide_frequency();
    });
}
function toggle_frequency(q_string, db_url, pathname) {
    var field =  $("#frequency_field").val();
    if (field != 'collocate') {
        var script_call = db_url + "/scripts/get_frequency.py?" + q_string + "&frequency_field=" + field;
    } else {
        var script_call = db_url + "/scripts/get_collocate.py?" + q_string
    }
    $(".loading").empty().hide();
    var spinner = '<img src="' + db_url + '/js/ajax-loader.gif" alt="Loading..."  height="25px" width="25px"/>';
    $(".results_container").animate({
        "margin-right": "410px"},
        150, function() {
                getCitationWidth();
            }
    );
    var width = $(".sidebar_display").width() / 2;
    $(".loading").append(spinner).css("margin-left", width).css("margin-top", "10px").show();
    $.getJSON(script_call, function(data) {
        var newlist = "";
        $(".loading").hide().empty();
        if (field == "collocate") {
            newlist += "<p class='freq_sidebar_status'>Collocates within 10 words left or right</p>";
        }
        $.each(data, function(index, item) {
            var url = '<a class="freq_sidebar_text" href="' + item[2] + '">' + item[0] + '</a>';
            newlist += '<li style="white-space:nowrap;">';
            newlist += '<span class="ui-icon ui-icon-bullet" style="display: inline-block;vertical-align:10px;"></span>';
            newlist += url + '<span style="float:right;display:inline-block;padding-right: 5px;">' + item[1] + '</span></li>';
        });
        $("#freq").hide().empty().html(newlist).fadeIn('fast');
    });
    $("#hide_frequency").show();
    $(".frequency_container").show();
    $("#hide_frequency").click(function() {
        hide_frequency();
    });
    sidebar_reports(q_string, db_url, pathname);
}
function hide_frequency() {
    $("#hide_frequency").hide();
    $("#freq").empty().hide();
    $('.frequency_container').hide();
    $(".loading").empty();
    $(".results_container").animate({
        "margin-right": "0px"},
        150, function() {
                getCitationWidth();
        }
    );
}