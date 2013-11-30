<div id="sidebar_area" style="float: right;margin-top: -8px;">
    <div id="sidebar_button" style="float: right;padding-top: 8px;">
        <select name="frequency_field" id='frequency_field'>
            % for facet in db.locals["metadata_fields"]:
                <%
                if "metadata_aliases" in db.locals and facet in db.locals["metadata_aliases"]:
                    alias = db.locals["metadata_aliases"][facet]
                else:
                    alias = facet
                %>
                <option value='${facet}'>Display frequency by <span style="font-weight: 700;">${alias}</span></option>
            % endfor
            <option value='collocate'>Display frequency by <span style="font-weight: 700;">collocates</span></option>
        </select>
    </div>
    <div id="sidebar_display">
        <div class="loading" style="display:none;z-index:99;position:absolute;margin-left:20px;"></div>
        <div id="hide_frequency">X</div>
        <div id="frequency_container">
            <ol id="frequency_table"></ol>
        </div>
    </div>
</div>