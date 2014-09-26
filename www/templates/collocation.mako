<%include file="header.mako"/>
<%include file="search_form.mako"/>
<script>
    var all_colloc = ${dumps(all_colloc)};
    var left_colloc = ${dumps(left_colloc)};
    var right_colloc = ${dumps(right_colloc)};
    var hit_len = ${hit_len};
</script>
<div class="container-fluid">    
    <div id='philologic_response' class="panel panel-default">
        <div id='initial_report'>
            <div id='description'>
                <button type="button" id="export-results" class="btn btn-default btn-xs pull-right" data-toggle="modal" data-target="#export-dialog">
                    Export results
                </button>
                <div id="search_arguments">
                    Displaying the top 100 collocates for <span id="colloc_hits">${hit_len}</span> occurrences of <b>${q['q'].decode('utf-8', 'ignore')}</b><br>
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
            <div id='philologic_collocation' class="row">
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
                            <% pos = 0 %>
                            % for all, left, right in order(all_colloc, left_colloc, right_colloc):
                                <% pos += 1 %>
                                <tr>
                                    <td>
                                        <span id="all_num${pos}">
                                            <span id="all_word_${pos}" data-word="${all[0]}" data-direction="all" data-count="${all[1]}">${all[0]}</span>
                                            <span id="all_count_${pos}">(${all[1]})</span>
                                        </span>
                                    </td>
                                    <td>
                                        <span id="left_num${pos}">
                                            <span id="left_word_${pos}" data-word="${left[0]}" data-direction="left" data-count="${left[1]}">${left[0]}</span>
                                            <span id="left_count_${pos}">(${left[1]})</span>
                                        </span>
                                    </td>
                                    <td>
                                        <span id="right_num${pos}">
                                            <span id="right_word_${pos}" data-word="${right[0]}" data-direction="right" data-count="${right[1]}">${right[0]}</span>
                                            <span id="right_count_${pos}">(${right[1]})</span>
                                        </span>
                                    </td>
                                </tr>
                            % endfor
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>
