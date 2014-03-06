$(document).ready(function() {
    
    
    // Check if dbname is configured, and if not set with a regex
    if ($("#main").data("dbname") != "notitle") {
        var title = $("#main").data("dbname");
    } else {
        var title = window.location.pathname.replace(/^\/[^/]+\/([^/]+)\/mobile\/philologic.html/, '$1');
    }
    $('h1.ui-title').text(title);
    
    // Show spinner on AJAX calls
    $(document).on({
        ajaxStart: function() { 
            $.mobile.loading('show');
        },
        ajaxStop: function() {
            $.mobile.loading('hide');
        }    
    });
    
    // Load all titles from database
    $.getJSON("../dispatcher.py/?report=bibliography&format=json", function(data) {
        var html = '<ul data-role="listview" style="margin-top: .5em;">';
        for (i in data) {
            html += '<li>' + data[i].citation + '</li>';
        }
        html += '</ul>';
        $('#browse_title').append(html).find('ul').listview();
        browseBibliography();
    });
    
    // Load titles when selecting the author tab
    $('#author_tab').click(function() {
        if ($('#browse_author').children().length == 0) {
            $.getJSON("../dispatcher.py/?report=bibliography&format=json&group_by_author=bibliography", function(data) {
                var html = '<ul data-role="listview" data-autodividers="true" data-filter="true" style="margin-top: .5em;">';
                for (i in data) {
                    html += '<li data-philoid=' + data[i].philo_id + '>' + i + '</li>';
                }
                html += '</ul>';
                $('#browse_author').append(html).find('ul').listview();
            });
        }
    });
    
    // Slide in/out search menu from the side
    $(document).on( "swipeleft swiperight", "#search", function( e ) {
        // We check if there is no open panel on the page because otherwise
        // a swipe to close the left panel would also open the right panel (and v.v.).
        // We do this by checking the data that the framework stores on the page element (panel: open).
        if ( $( ".ui-page-active" ).jqmData( "panel" ) !== "open" ) {
            if ( e.type === "swiperight" ) {
                $( "#left-panel" ).panel( "open" );
            }
        } else if (e.type === "swipeleft") {
            $( "#left-panel" ).panel( "close" );
        }
    });
    
    $('#philo_search').submit(function(e) {
        e.preventDefault();
        var script = "../dispatcher.py/?method=proxy&arg_proxy=&arg_phrase=&title=&author=&create_date=&head=&n=&id=&word_num=5&start_date=&end_date=&year_interval=10&pagenum=25&format=json";
        var q = $('#search-1').val();
        var report = $('input[name=report]:checked').attr('value');
        $( "#left-panel" ).panel( "close" );
        if (report == "concordance") {
            concordanceSearch(script, q, report);
        } else if (report == "frequency") {
            var field = $('input[name=frequency_type]:checked').attr('value');
            frequencySearch(script, q, report, field);
        } else if (report == "bibliography") {
            browseBibliography();
        }
        $('#back_kwic, #back_concordance, #back_navigation, #back_frequency').click(function() {
            var div_to_clear = $(this).data('clear');
            $('#' + div_to_clear).empty();
        });
    });
    $('input[name=report]').click(function() {
        var report_selected = $(this).val();
        if (report_selected == "frequency") {
            $('#frequency_options').css({'opacity': 100, 'max-height': '51px'});
        } else if (report_selected == "bibliography") {
            $('#bibliography_choice').show();
        } else {
            $('#frequency_options').css({'opacity': 0, 'max-height': 0});
            $('#bibliography_choice').hide();
        }
    });
    $('#highlight_button').click(function() {
        $.mobile.silentScroll($('#navigation .highlight').offset().top - 40);
        $('.highlight').addClass('highlight-background').css({'background-color': '#DB7077', 'color': '#fff'});
        setTimeout(function() {
            $('.highlight-background').css({'background-color': '#fff', 'color': '#DB7077'});
        }, 300);
    });
    $('#top_navigation').click(function() {
        $.mobile.silentScroll(0);
    });
});

function browseBibliography() {
    $('.biblio_cite').click(function() {
        var philo_id = $(this).data('id');
        var script = "../scripts/get_table_of_contents.py?format=json&philo_id=" + philo_id;
        console.log(script)
        $.getJSON(script, function(data) {
            $('#toc_navigation').html(data);
            console.log(data)
        });
        $.mobile.pageContainer.pagecontainer("change", $("#table_of_contents"), {transition: "slide"});
    })
}

function concordanceSearch(script, q, report) {
    script += "&q=" + q + "&report=" + report;
    $.getJSON(script, function(data) {
        var html = '<h4>Concordance Results:</h4><ul data-role="listview" data-inset="true">';
        for (var i=0; i< data.length; i++) {
            var number = '<span style="width: 40px;font-size: .8em">' + (i+1) + "</span>&nbsp";
            html += '<li data-role="list-divider">' + number + data[i].citation + '</li>'
            html += '<li>' + data[i]['text'] + '</li>';
        }
        html += '</ul>'
        $("#concordance div:jqmData(role=content)").append(html);
        $('#concordance').find('ul').listview();
        $('.philologic_cite a').tap(function(e) {
            e.preventDefault();
            e.stopPropagation();
            var href = $(this).attr("href") + '&format=json';
            $.mobile.loader({ defaults: true });
            $.getJSON(href, function(data) {
                $("#navigation div:jqmData(role=content)").append(data);
                $.mobile.pageContainer.pagecontainer("change", $("#navigation"), {transition: "slide"});
            });
        });
        $.mobile.pageContainer.pagecontainer("change", $("#concordance"), {transition: "slide"});
    });
}

function frequencySearch(script, q, report, field) {
    script += "&q=" + q + "&report=" + report + "&field=" + field;
    $.getJSON(script, function(data) {
        var length = data.length;
        var field = data.field;
        var html = '<table data-role="table" id="frequency_table" class="table-stroke my-custom-breakpoint">';
        html += '<thead><tr><th id="frequency_label">' + field + '</th><th>Count</th></tr></thead>';
        html += '<tbody>';
        for (var i=0; i < data.result.length; i++) {
            html += "<tr>";
            html += '<td><span data-url="' + data.result[i].url + '">' + data.result[i].label + '</span></td>';
            html += '<td>' + data.result[i].count + '</td>';
        }
        html += '</tbody></table>';
        $("#frequency div:jqmData(role=content)").append(html);
        $('#frequency_table').table().table("refresh");
        $.mobile.pageContainer.pagecontainer("change", $("#frequency"), {transition: "slide"});
    });
}