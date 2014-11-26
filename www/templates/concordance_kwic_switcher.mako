<div id="report_switch" class="btn-group">
    % if report == "concordance":
        <button type="button" class="btn btn-primary active" id="concordance-switch" data-script="${ajax['concordance']}" data-report="concordance">
    % else:
        <button type="button" class="btn btn-primary" id="concordance-switch" data-script="${ajax['concordance']}" data-report="concordance">
    % endif
            <span class="hidden-xs hidden-sm">View occurrences with context</span>
            <span class="visible-xs visible-sm">Concordance</span>
        </button>
    % if report == "concordance":
        <button type="button" class="btn btn-primary" id="kwic-switch" data-script="${ajax['kwic']}" data-report="kwic">
    % else:
        <button type="button" class="btn btn-primary active" id="kwic-switch" data-script="${ajax['kwic']}" data-report="kwic">
    % endif
            <span class="hidden-xs hidden-sm">View occurrences line by line (KWIC)</span>
            <span class="visible-xs visible-sm">Keyword in context</span>
        </button>
</div>