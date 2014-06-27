<div id="sidebar_area">
    <ul id="sidebar_button">
        <li id="frequency_by" style='margin-right: 0px;margin-top:-3px;display: inline-block;'>
            <select id="select_facet">
                <optgroup label="Frequency by metadata field">
                    % for pos, facet in enumerate(config["facets"]):
                        <%
                        if facet in config["metadata_aliases"]:
                            alias = config["metadata_aliases"][facet]
                        else:
                            alias = facet
                        %>
                        % if pos == 0:
                            <option selected="selected" class="sidebar_option" id="side_opt_${facet}" value='${facet}' data-display='${facet}'>Display frequency by ${alias}</option>
                        % else:
                            <option class="sidebar_option" id="side_opt_${facet}" value='${facet}' data-display='${facet}'>Display frequency by ${alias}</option>
                        % endif
                    % endfor
                </optgroup>
                % if report != 'bibliography':
                    <optgroup label="Collocate of query">
                        <option class="sidebar_option" id="side_opt_collocate" value='collocation_report' data-display='collocate'>Display collocates of query term(s)</option>
                    </optgroup>
                % endif
            </select>
        </li>
        <li id="hide_sidebar">X</li>
    </ul>
    <div id="sidebar_display">
        <div id="frequency_container">
            <div id="progress_bar">
                <div class="progress-label"></div>
            </div>
            <ol id="frequency_table"></ol>
        </div>
    </div>
</div>