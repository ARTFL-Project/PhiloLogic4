<%include file="header.mako"/>
<script>	  	
$(document).ready(function() {
    $("#report").show();
    showHide('concordance');
    $("#search_elements").show();
    $("#hide_search_form").hide();
    $("#form_separation").hide();
});	  	
</script>
<%include file="search_boxes.mako"/>
<%include file="footer.mako"/>
