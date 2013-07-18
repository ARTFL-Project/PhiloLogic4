<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script>
$(document).ready(function() {
    $("#form_body").hide();
});
</script>
<div id="error_container" style="max-width:500px !important;font-size:120%;">
    <div id="error_message" class="ui-state-error" style="text-align:justify;padding: 5px 5px 5px 5px;">
        <span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>
        We've encountered an error with your search. The issue has been
        logged and will be fixed as soon as possible.
    </div>
    <p><a href="${db.locals['db_url']}/">Return to search form</a></p>
</div>
<%include file="footer.mako"/>
