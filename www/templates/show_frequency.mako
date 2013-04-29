<div class="sidebar_display">
    <div class="show_frequency">
        <span id="toggle_frequency">
            <span id="freq_sidebar"><label for="freq_sidebar">Display frequency by</label></span>
        </span>
        <label class="custom-select">
            <select name="frequency_field" id='frequency_field'>
                % for facet in db.locals["metadata_fields"]:
                    <option value='${facet}'>${facet}</option>
                % endfor
                    <option value='collocate'>collocate</option>
            </select>
        </label>
    </div>
    <div class="loading" style="display:none;z-index:99;position:absolute;margin-left:20px;"></div>
    <div class="frequency_container">
        <span class="hide_frequency" style="display:none;">X</span>
        <div id="freq" class="frequency_table"></div>
    </div>
</div>