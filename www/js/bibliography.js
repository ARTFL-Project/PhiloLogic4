$(document).ready(function() {
    $('.results_container').show()
    $('.sidebar_display').css('margin-top', '-29px');
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = db_locals['db_url'];
    var q_string = window.location.search.substr(1);
    sidebar_reports(q_string, db_url, pathname);
})