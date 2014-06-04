$(document).ready(function() {
    
    $('#page_links').find('a').each(function(){$(this).button()});
    
    $('#form_body').hide();
    $('.close_concordance').hide();
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = webConfig['db_url'];
    var q_string = window.location.search.substr(1);
    getCitationWidth()
    $(window).resize(function() {
        getCitationWidth();
    });
    //sidebar_reports(q_string, db_url, pathname);
    //$('#colloc_in_hits').append(occurences);
    $('#return_to_colloc').click(function() {
        History.back();
    });
    $('.more_context').hide();
    //$(window).load(function() {
    //    fetchMoreContext();
    //});
});
