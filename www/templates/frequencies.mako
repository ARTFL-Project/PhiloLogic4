<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div id='philologic_response'>
    <div id='initial_report'>
        <p id='description'>
        Frequencies for
        % for field in q['metadata']:
            <br>${field}: ${q['metadata'][field]}
        % endfor
        </p>
    </div>
    <div id="results_container">
        % for i in results:
            ${i.decode('utf-8')}
        % endfor
    </div>
</div>
<%include file="footer.mako"/>