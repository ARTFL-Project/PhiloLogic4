<%include file="header.mako"/>
<script>	  	
$(document).ready(function() {
    $("#report").show();
    showHide('concordance');
    $("#search_elements").show();
    $(".more_options").hide();
    $("#form_separation").hide();
});	  	
</script>
<%include file="search_boxes.mako"/>
<%include file="footer.mako"/>
