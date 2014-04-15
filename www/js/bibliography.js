$(document).ready(function() {
    
    // jQueryUI theming
    $('#page_links').find('a').each(function(){$(this).button()});
    
    var new_url = window.location.href.replace(/report=concordance/, 'report=bibliography');
    History.pushState(null, '', new_url);
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = webConfig['db_url'];
    var q_string = window.location.search.substr(1);
    $('#sidebar_area').css('margin-top', '-42px');
    $('#sidebar_button').css('margin-top', '-1px');
    $('#frequency_field').css('top', '253px');
    sidebar_reports(q_string, db_url, pathname);
})