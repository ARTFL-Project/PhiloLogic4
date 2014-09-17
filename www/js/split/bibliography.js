"use strict";

$(document).ready(function() {
    var new_url = window.location.href.replace(/report=concordance/, 'report=bibliography');
    History.pushState(null, '', new_url);
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = webConfig['db_url'];
    var q_string = window.location.search.substr(1);
    sidebarReports(q_string, db_url, pathname);
});