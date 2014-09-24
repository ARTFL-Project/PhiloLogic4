<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div class="container-fluid">
    <div id='philologic_response'>
        <div id='initial_report' class="row">
            <div class="col-xs-12">
                <div class="panel panel-default">
                    <div id='description'>
                        <button type="button" id="export-results" class="btn btn-default btn-xs pull-right" data-toggle="modal" data-target="#export-dialog">
                            Export results
                        </button>
                        <div id="search_arguments" data-start="${q['start_date']}" data-end="${q['end_date']}", data-interval="${q['year_interval']}">
                            ${total} occurrences for <b>${q['q'].decode('utf_8')}</b><br>
                            Bibliographic criteria: ${biblio_criteria or "<b>None</b>"}<br>
                            Use of the term(s) between
                            <span class="biblio-criteria"><b>${q['start_date']}</b>
                                <span class="glyphicon glyphicon-remove-circle remove_metadata" id="remove_metadata_date_start"></span>
                            </span>&nbsp and
                            <span class="biblio-criteria"><b>${q['end_date']}</b>
                                <span class="glyphicon glyphicon-remove-circle remove_metadata" id="remove_metadata_date_end"></span>
                            </span>
                        </div>
                    </div>
                    <div id="progress_bar" style="margin-top:-5px;margin-bottom: 10px" data-total='${total}'>
                        <div class="progress-label"></div>
                    </div>
                    <div id="time_series_buttons" class="btn-group" data-toggle="buttons">
                        <label class="btn btn-primary active" id="absolute_time" data-value='${frequencies}' data-interval="${q['year_interval']}" checked="checked">
                            <input type="radio" name="freq_type" >
                            Absolute Frequency
                        </label>
                        <label class="btn btn-primary" disabled="disabled" id="relative_time" data-datecount='${date_counts}' data-interval="${q['year_interval']}">
                            <input type="radio" name="freq_type">
                            Relative Frequency
                        </label>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-xs-12">
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
        </div>
    </div>
</div>
<%include file="footer.mako"/>