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