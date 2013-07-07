<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script>
$(document).ready(function() {
    collocation_cloud();
    var all_colloc = ${dumps(all_colloc)};
    var left_colloc = ${dumps(left_colloc)};
    var right_colloc = ${dumps(right_colloc)};
    var db_url = db_locals['db_url'];
    update_colloc(db_url, all_colloc, left_colloc, right_colloc, ${hit_len}, 0, 100);
    var spinner = '<img src="' + db_url + '/js/ajax-loader.gif" alt="Loading..."  height="25px" width="25px"/>';
    $('#working').append(spinner);
})
</script>
<div class='philologic_response'>
    <div class='initial_report'>
        <p class='description'>
            Displaying the top 100 collocates for ${hit_len} occurrences of "${q['q'].decode('utf-8', 'ignore')}":
        </p>
        The 200 most common words are being filtered from this report.
        <span id="working" style="font-weight:600;"></span>
    </div>
    <div class="results_container">
        <div class='philologic_collocation'>
            <div id="word_cloud" class="word_cloud">
                <div id="collocate_counts" class="collocation_counts">
                </div>
            </div>
            <table class="philologic_table" id="collocation_table">
                <tr>
                 <th class="table_header">within ${q['word_num']} words on either side</th>
                 <th class="table_header">within ${q['word_num']} words to left</th>
                 <th class="table_header">within ${q['word_num']} words to right</th>
                </tr>
                <% pos = 0 %>
                % for all, left, right in order(all_colloc, left_colloc, right_colloc):
                    <% pos += 1 %>
                    <tr>
                        <td class="table_column">
                            <span id="all_num${pos}">
                                <a href="${link(q, all[0], 'all', all[1])}">${all[0]}</a>
                                <span id="all_count_${pos}">(${all[1]})</span>
                            </span>
                        </td>
                        <td class="table_column">
                            <span id="left_num${pos}">
                                <a href="${link(q, left[0], 'left', left[1])}">${left[0]}</a>
                                <span id="left_count_${pos}">(${left[1]})</span>
                            </span>
                        </td>
                        <td class="table_column">
                            <span id="right_num${pos}">
                                <a href="${link(q, right[0], 'right', right[1])}">${right[0]}</a>
                                <span id="right_count_${pos}">(${right[1]})</span>
                            </span>
                        </td>
                    </tr>
                % endfor
            </table>
        </div>
    </div>
</div>
<%include file="footer.mako"/>
