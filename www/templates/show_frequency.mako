<div id="sidebar_area">
    <ul id="sidebar_button">
        <li id="frequency_by" style='margin-right: 0px;display: inline-block;'>
            Display frequency by <span id="displayed_sidebar_value">${db.locals["metadata_fields"][0]}</span>
            <span style="vertical-align: middle;font-size: 60%;margin-right: 0;">&nbsp&nbsp&nbsp&#9660;</span>
        </li>
        <li id="hide_sidebar">X</li>
    </ul>
    
    <ol id="frequency_field">
        % for facet in db.locals["metadata_fields"]:
            <%
            if "metadata_aliases" in db.locals and facet in db.locals["metadata_aliases"]:
                alias = db.locals["metadata_aliases"][facet]
            else:
                alias = facet
            %>
            <li class="sidebar_option" id="side_opt_${facet}" data-value='${facet}' data-display='${facet}'>Display frequency by <span style="font-weight: 700;">${alias}</span></li>
        % endfor
        % if report != 'bibliography':
            <li class="sidebar_option" id="side_opt_collocate" data-value='collocation_report' data-display='collocate'>Display <span style="font-weight: 700;">collocates</span></li>
        % endif
    </ol>
    <div id="sidebar_display">
        <div id="frequency_container">
            <div id="progress_bar">
                <div class="progress-label"></div>
            </div>
            <ol id="frequency_table"></ol>
        </div>
    </div>
</div>