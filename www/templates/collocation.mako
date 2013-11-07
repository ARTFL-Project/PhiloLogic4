<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script>
var all_colloc = ${dumps(all_colloc)};
var left_colloc = ${dumps(left_colloc)};
var right_colloc = ${dumps(right_colloc)};
var hit_len = ${hit_len};
</script>
<script type="text/javascript" src="${db.locals['db_url']}/js/jquery.tagcloud.js"></script>
<script type="text/javascript" src="${db.locals['db_url']}/js/collocation.js"></script>
<div id='philologic_response'>
    <div id='initial_report'>
        <p id='description'>
            Displaying the top 100 collocates for <span id="colloc_hits">${hit_len}</span> occurrences of "${q['q'].decode('utf-8', 'ignore')}":
        </p>
        <div id="progress_bar" style="position:absolute;margin-top:-15px;">
            <div class="progress-label"></div>
        </div>
        The 100 most common words are being filtered from this report.
    </div>
    <div class="results_container">
        <div id='philologic_collocation'>
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
