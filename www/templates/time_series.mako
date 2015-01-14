<%include file="header.mako"/>
% if not config.dictionary:
    <%include file="search_form.mako"/>
% else:
    <%include file="dictionary_search_form.mako"/>
% endif
<% query = time_series['query'] %>
<div class="container-fluid">
    <div id='philologic_response'>
        <div id='initial_report' class="row">
            <div class="col-xs-12">
                <div class="panel panel-default">
                    <div id='description'>
                        <button type="button" id="export-results" class="btn btn-default btn-xs pull-right" data-toggle="modal" data-target="#export-dialog">
                            Export results
                        </button>
                        <div id="search_arguments" data-start="${query['start_date']}" data-end="${query['end_date']}", data-interval="${query['year_interval']}" data-script="${ajax['total_hits']}">
                            <span id="time-series-length">
                                % if time_series['query_done']:
                                    ${time_series['results_length']}
                                % else:
                                    Still working...
                                % endif
                            </span> occurrences for <b>${query['q'].decode('utf_8')}</b><br>
                            Bibliographic criteria: ${biblio_criteria or "<b>None</b>"}<br>
                            Use of the term(s) between
                            <span class="biblio-criteria"><b>${query['start_date']}</b>
                                <span class="glyphicon glyphicon-remove-circle remove_metadata" id="remove_metadata_date_start"></span>
                            </span>&nbsp and
                            <span class="biblio-criteria"><b>${query['end_date']}</b>
                                <span class="glyphicon glyphicon-remove-circle remove_metadata" id="remove_metadata_date_end"></span>
                            </span>
                        </div>
                        % if config['debug']:
                            % if "error" in time_series:
                                <div class="bg-danger" style="margin-top: 20px; width: 50%;">${time_series['error']}</div>
                            % endif
                        % endif
                    </div>
                    <div class="progress" style="margin-left: 15px; margin-right: 15px; margin-top: -10px;">
                        <div class="progress-bar" role="progressbar" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" data-total="${time_series['results_length']}" style="width: 0%;">
                        </div>
                    </div>
                    <div id="time_series_buttons" class="btn-group" data-toggle="buttons">
                        <label class="btn btn-primary active" id="absolute_time" data-value='${json.dumps(time_series['results']['absolute_count'])}' data-interval="${query['year_interval']}" checked="checked">
                            <input type="radio" name="freq_type" >
                            Absolute Frequency
                        </label>
                        <label class="btn btn-primary" disabled="disabled" id="relative_time" data-datecount='${json.dumps(time_series['results']['date_count'])}' data-interval="${query['year_interval']}">
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
                    <div id='time_series_report' style='display:none;' data-script="${ajax['time_series']}" data-status="json.dumps(time_series['results_done']})">
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