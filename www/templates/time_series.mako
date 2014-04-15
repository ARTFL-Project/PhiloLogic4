<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div id='philologic_response'>
    <div id='initial_report'>
        <div id='description'>
            <div id="search_arguments">
                Use of the term(s) <b>${q['q'].decode('utf_8')}</b> between
                <span class="biblio_criteria"><b>${q['start_date']}</b>
                    <span class="ui-icon ui-icon-circle-close" id="remove_metadata_date_start"></span>
                </span>&nbsp and
                <span class="biblio_criteria"><b>${q['end_date']}</b>
                    <span class="ui-icon ui-icon-circle-close" id="remove_metadata_date_end"></span>
                </span>
                <br>
                Bibliographic criteria: ${biblio_criteria or "<b>None</b>"}
            </div>
        </div>
        <div id="progress_bar" style="margin-top:-5px;margin-bottom: 10px" data-total='${total}'>
            <div class="progress-label"></div>
        </div>
        <div id="time_series_buttons">
            <input type="radio" name="freq_type" id="absolute_time" data-value='${frequencies}' data-interval="${q['year_interval']}" checked="checked">
            <label for="absolute_time">Absolute Frequency</label>
            <input type="radio" name="freq_type" id="relative_time" data-datecount='${date_counts}' data-interval="${q['year_interval']}">
            <label for="relative_time">Relative Frequency</label>
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