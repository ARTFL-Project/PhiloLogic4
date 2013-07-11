<div class="sidebar_display">
    <div class="show_frequency">
        <span id="toggle_frequency">
            <span id="freq_sidebar"><label for="freq_sidebar">Display frequency by</label></span>
        </span>
        <label class="custom-select">
            <select name="frequency_field" id='frequency_field'>
                % for facet in db.locals["metadata_fields"]:
                    <%
                    if "metadata_aliases" in db.locals and facet in db.locals["metadata_aliases"]:
                        alias = db.locals["metadata_aliases"][facet]
                    else:
                        alias = facet
                    %>
                    <option value='${facet}'>${alias}</option>
                % endfor
                <option value='collocate'>Collocates</option>
            </select>
        </label>
    </div>
    <div class="loading" style="display:none;z-index:99;position:absolute;margin-left:20px;"></div>
    <div class="hide_frequency" style='display:none;'>X</div>
    <div class="frequency_container">
        <div id="freq" class="frequency_table"></div>
    </div>
</div>