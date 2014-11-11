<div id="report_switch" class="btn-group">
    <%
    concordance_script = "%s/scripts/concordance_kwic_switcher.py?%s" % (config.db_url, q['q_string'].replace('report=kwic', 'report=concordance'))
    kwic_script = "%s/scripts/concordance_kwic_switcher.py?%s" % (config.db_url, q['q_string'].replace('report=concordance', 'report=kwic'))
    %>
    % if report == "concordance":
        <button type="button" class="btn btn-primary active" id="concordance-switch" data-script="${concordance_script}" data-report="concordance">
    % else:
        <button type="button" class="btn btn-primary" id="concordance-switch" data-script="${concordance_script}" data-report="concordance">
    % endif
            View occurences with context
        </button>
    % if report == "concordance":
        <button type="button" class="btn btn-primary" id="kwic-switch" data-script="${kwic_script}" data-report="kwic">
    % else:
        <button type="button" class="btn btn-primary active" id="kwic-switch" data-script="${kwic_script}" data-report="kwic">
    % endif
            View occurences line by line (KWIC)
        </button>
</div>