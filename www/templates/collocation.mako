<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script>
$(document).ready(function() {
    var all_colloc = ${dumps(all_colloc)};
    var left_colloc = ${dumps(left_colloc)};
    var right_colloc = ${dumps(right_colloc)}
    update_colloc(all_colloc, left_colloc, right_colloc, ${hit_len}, 0, 100);
    $('#working').each(function() {
        var elem = $(this);
        setInterval(function() {
            if (elem.css('visibility') == 'hidden') {
                elem.css('visibility', 'visible');
            } else {
                elem.css('visibility', 'hidden');
            }    
        }, 750);
    });
})
</script>
<div class='philologic_response'>
    <div class='initial_report'>
        <p class='description'>
            Displaying the top 100 collocates of "${q['q'].decode('utf-8', 'ignore')}":
        </p>
        The 100 most common words are being filtered from this report.
        <span id="working" style="font-weight:600;">Still working...</span>
    </div>
    <div class="results_container">
        <div class='philologic_collocation'>
            <table class="philologic_table">
                <colgroup span="3"></colgroup>
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
                                (${all[1]})
                            </span>
                        </td>
                        <td class="table_column">
                            <span id="left_num${pos}">
                                <a href="${link(q, left[0], 'left', left[1])}">${left[0]}</a>
                                (${left[1]})
                            </span>
                        </td>
                        <td class="table_column">
                            <span id="right_num${pos}">
                                <a href="${link(q, right[0], 'right', right[1])}">${right[0]}</a>
                                (${right[1]})
                            </span>
                        </td>
                    </tr>
                % endfor
            </table>
        </div>
    </div>
</div>
<%include file="footer.mako"/>
