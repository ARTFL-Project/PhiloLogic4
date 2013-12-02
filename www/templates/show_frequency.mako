<div id="sidebar_area" style="float: right;margin-top: -8px;">
    <div id="sidebar_button" style="float: right;padding-top: 8px;">

        <div id="frequency_by" style="white-space: nowrap;margin-right: 0px;">
            Display frequencies by <span id="displayed_sidebar_value">${db.locals["metadata_fields"][0]}</span>
            &nbsp&nbsp&nbsp<span style="display: inline-block;vertical-align: middle;font-size: 50%;">&#9660;</span>
        </div>
        <ol id="frequency_field">
            % for facet in db.locals["metadata_fields"]:
                <%
                if "metadata_aliases" in db.locals and facet in db.locals["metadata_aliases"]:
                    alias = db.locals["metadata_aliases"][facet]
                else:
                    alias = facet
                %>
                <li class="sidebar_option" id="side_opt_${facet}" data-value='${facet}'>Display frequency by <span style="font-weight: 700;">${alias}</span></li>
            % endfor
            <li class="sidebar_option" id="side_opt_collocate" data-value='collocate'>Display <span style="font-weight: 700;">collocates</span></li>
        </ol>
    </div>
    <div id="sidebar_display">
        <div class="loading" style="display:none;z-index:99;position:absolute;margin-left:20px;"></div>
        <div id="hide_frequency">X</div>
        <div id="frequency_container">
            <ol id="frequency_table"></ol>
        </div>
    </div>
</div>