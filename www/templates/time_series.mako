<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script type="text/javascript" src="https://www.google.com/jsapi"></script>
<script type="text/javascript" src="${db.locals['db_url']}/js/timeSeries.js"></script>
<div id='philologic_response'>
    <div id='initial_report'>
        <p id='description'>
            Use of the term(s) "${q['q'].decode('utf_8')}" throughout time
        </p>
        <div id="time_series_buttons">
                <input type="radio" name="freq_type" id="relative_time" data-value='${relative_frequencies}' data-interval="${q['year_interval']}" checked="checked">
                <label for="relative_time">Average Use</label>
                <input type="radio" name="freq_type" id="absolute_time" data-value='${frequencies}' data-interval="${q['year_interval']}">
                <label for="absolute_time">Total Use</label>
            </div>
    </div>
    <div class="results_container">
        <div id='time_series_report' style='display:none;'>
            <div id="chart" style="width: 900px; height: 500px;"></div>
        </div>
        <div id="test_time_series">
            <div id="top_division">
                <div id='top_number'></div>
            </div>
            <div id="middle_division">
                <div id="middle_number"></div>
            </div>
            <div id="first_division">
                <div id="first_number"></div>
            </div>
            <div id="side_text"></div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>