<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script type="text/javascript" src="https://www.google.com/jsapi"></script>
<script type="text/javascript">
google.load("visualization", "1", {packages:["corechart"]});
$(document).ready(function(){
    var mydata = eval($("#relative_time").val());
    google.setOnLoadCallback(drawChart(mydata, "Rate per 10000 words"));
    $('#absolute_time').click(function() {
        var mydata = eval($(this).val());
        $("#chart").fadeOut('fast').empty().show();
        google.setOnLoadCallback(drawChart(mydata,"Count"));
        $("#chart").hide().fadeIn('fast');
    });
    $('#relative_time').click(function() {
        var mydata = eval($(this).val());
        $("#chart").fadeOut('fast').empty().show();
        google.setOnLoadCallback(drawChart(mydata,"Rate per 10000 words"));
        $("#chart").hide().fadeIn('fast');
    });
});
function drawChart(mydata, count_type) {
    var data = google.visualization.arrayToDataTable(mydata);
    var chart = new google.visualization.ColumnChart(document.getElementById('chart'));
    var options = {
      hAxis: {title: 'Date', titleTextStyle: {color: 'black'}},
      vAxis: {title: count_type, titleTextStyle: {color: 'black'}}
    }
    chart.draw(data, options);
}
</script>
<div class='philologic_response'>
    <div class='initial_report'>
        <p class='description'>
            Use of the term(s) "${q['q'].decode('utf_8')}" throughout time
        </p>
    </div>
    <div class="results_container">
        <div class='time_series_report'>
            <div id="time_series_buttons">
                <input type="radio" name="freq_type" id="relative_time" value='${relative_frequencies}' checked="checked">
                <label for="relative_time">Relative frequency</label>
                <input type="radio" name="freq_type" id="absolute_time" value='${frequencies}'>
                <label for="absolute_time">Absolute frequency</label>
            </div>
            <div id="chart" style="width: 900px; height: 500px;"></div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>