<%include file="header.mako"/>
% if not config.dictionary:
    <%include file="search_form.mako"/>
% else:
    <%include file="dictionary_search_form.mako"/>
% endif
<script>
    var all_collocates = ${dumps(dict(collocation['all_collocates']))};
    var left_collocates = ${dumps(dict(collocation['left_collocates']))};
    var right_collocates = ${dumps(dict(collocation['right_collocates']))}
    var hit_len = ${collocation['results_length']};
</script>
<div class="container-fluid">    
    <div id='philologic_response' class="panel panel-default">
        <div id='initial_report'>
            <div id='description'>
                <button type="button" id="export-results" class="btn btn-default btn-xs pull-right" data-toggle="modal" data-target="#export-dialog">
                    Export results
                </button>
                <div id="search_arguments">
                    Displaying the top 100 collocates for <span id="colloc_hits">${collocation['results_length']}</span> occurrences of <b>${collocation['query']['q'].decode('utf-8', 'ignore')}</b><br>
                    Bibliographic criteria: ${biblio_criteria or "<b>None</b>"}
                </div>
            </div>
            <div class="progress" style="margin-left: 15px; margin-right: 15px">
                <div class="progress-bar" role="progressbar" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">
                </div>
            </div>
            <div style="padding-left: 15px;">
                The 100 most common words are being filtered from this report.
            </div>
        </div>
        <div class="results_container">
            <div id='philologic_collocation' class="row" data-script="${config.db_url + '/scripts/get_collocation.py?' + collocation['query']['q_string']}" data-hits-length="${collocation['results_length']}">
                <div class="col-xs-12 col-sm-3 col-sm-push-9 col-md-4 col-md-push-8">
                    <div id="word_cloud" class="word_cloud">
                        <div id="collocate_counts" class="collocation_counts">
                        </div>
                    </div>
                </div>
                <div class="col-xs-12 col-sm-9 col-sm-pull-3 col-md-8 col-md-pull-4">
                    <div class="table-reponsive">
                        <table class="table table-bordered" id="collocation_table">
                            <tr>
                             <th>within ${q['word_num']} words on either side</th>
                             <th>within ${q['word_num']} words to left</th>
                             <th>within ${q['word_num']} words to right</th>
                            </tr>
                            <tr>
                                <td id="all-collocate-column">
                                </td>
                                <td id="left-collocate-column">
                                </td>
                                <td id="right-collocate-column">
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>
