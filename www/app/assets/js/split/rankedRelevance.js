$(document).ready(function() {
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = db_locals['db_url'];
    var q_string = window.location.search.substr(1);
    $('.sidebar_display').css('margin-top', '10px');
    display_options_on_selected();
    sidebar_reports(q_string, db_url, pathname);
});