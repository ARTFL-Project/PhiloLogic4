<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<div class='philologic_response'>
    <div id='initial_report'>
        <p id='description'>
            Frequency by ${frequency_field}
        </p>
        Top 100 ${frequency_field}s displayed
        <div id="frequency_report_switch" class="report_switch">
            <input type="radio" name="freq_switch" id="abs_freq_switch" value="?${q['q_string'].replace('&rate=relative', '')}" checked="checked">
            <label for="abs_freq_switch">View total counts</label>
            <input type="radio" name="freq_switch" id="rel_freq_switch" value="?${q['q_string'] + '&rate=relative'}">
            <label for="rel_freq_switch">View an average count per 10,000 words</label>
        </div>
    </div>
    <div id="results_container" class="results_container">
        <div class='philologic_frequency_report'>
            <table border="1" class="philologic_table">
                <tr>
                    <th class="table_header">${frequency_field}</th>
                    <th class="table_header">count</th>
                </tr>
                % for field,count,url in counts:
                    <tr>
                        <td class="table_column"><a href='${url}'>${field}</a></td>
                        <td class="table_column">${count}</td>
                    </tr>
              % endfor
            </table>
        </div>
    </div>
</div>
<%include file="footer.mako"/>