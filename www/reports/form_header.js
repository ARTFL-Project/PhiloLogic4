<script type="text/javascript">
function monkeyPatchAutocomplete() {
    //taken from http://stackoverflow.com/questions/2435964/jqueryui-how-can-i-custom-format-the-autocomplete-plug-in-results    
    
    // don't really need this, but in case I did, I could store it and chain
    var oldFn = $.ui.autocomplete.prototype._renderItem;

    $.ui.autocomplete.prototype._renderItem = function( ul, item) {
        // This regex took some fiddling but should match beginning of string and
        // any match preceded by a string: this is useful for sql matches.
        var re = new RegExp('((^' + this.term + ')|( ' + this.term + '))', "gi") ; 
        var t = item.label.replace(re,"<span style='font-weight:bold;color:Red;'>" + 
                "$&" + 
                "</span>");
        return $( "<li></li>" )
            .data( "item.autocomplete", item )
            .append( "<a>" + t + "</a>" )
            .appendTo( ul );
    };
}

function autocomplete_metadata(metadata, field) {
    $("#" + field).autocomplete({
        source: "/philo4/${dbname}/scripts/metadata_list.py?field=" + field,
        minLength: 2,
        dataType: "json"
    });
}

var fields = ${repr(db.locals['metadata_fields'])}
$(document).ready(function(){
    
    monkeyPatchAutocomplete();    
    
    $("#q").autocomplete({
        source: "/philo4/${dbname}/scripts/term_list.py",
        minLength: 2,
        "dataType": "json"
    });
    for (i in fields) {
        var  metadata = $("#" + fields[i]).val();
        var field = fields[i];
        autocomplete_metadata(metadata, field)
    }
//    The following is to display the right options when using the back button
    if ($("#report option[value='concordance']").attr('selected')) {
        $("#frequency").hide()
        $("#collocation").hide()
        $("#results_per_page").show()
    }
    if ($("#report option[value='kwic']").attr('selected')) {
        $("#frequency").hide()
        $("#collocation").hide()
        $("#results_per_page").show()
    }
    if ($("#report option[value='collocation']").attr('selected')) {
        $("#frequency").hide()
        $("#results_per_page").hide()
        $("#collocation").show()
    }
    if ($("#report option[value='frequency']").attr('selected')) {
        $("#collocation").hide()
        $("#results_per_page").hide()
        $("#frequency").show()
    }
    if ($("#report option[value='relevance']").attr('selected')) {
        $("#frequency").hide()
        $("#collocation").hide()
        $("#results_per_page").show()
    }
});

function showHide(value) {
    if (value == 'frequency') {
        $("#collocation").hide()
        $("#results_per_page").hide()
        $("#frequency").show()
    }
    if (value == 'collocation') {
        $("#frequency").hide()
        $("#results_per_page").hide()
        $("#collocation").show()
    }
    if (value == 'concordance' || value == 'kwic' || value == 'relevance') {
        $("#frequency").hide()
        $("#collocation").hide()
        $("#results_per_page").show()
    }
}

</script>