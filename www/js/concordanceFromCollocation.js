$(document).ready(function() {
    $('#form_body').hide();
    $('.philologic_response').css('margin-top', '0px');
    more_context();
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = db_locals['db_url'];
    var q_string = window.location.search.substr(1);
    sidebar_reports(q_string, db_url, pathname);
    $('#colloc_in_hits').append(occurences);
    $('.return_to_colloc').click(function() {
        History.back();
    });
});