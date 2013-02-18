
<div class="sidebar_display">
<span id="toggle_frequency" class="show_frequency">
<span id="freq_sidebar"><label for="freq_sidebar">Display frequency by</label></span>
</span>
<a href="javascript:void(0)" class="hide_frequency" style="display:none;">X</a>
<label class="custom-select">
<select id='frequency_field'>
% for facet in db.locals["metadata_fields"]:
    <option value='${facet}'>${facet}</option>
% endfor
    <option value='collocate'>collocate</option>
</select>
</label>
<div class="loading" style="display:none;z-index:99;position:absolute;margin-left:20px;"></div>
<div id="freq" class="frequency_table" style="display:none;"></div>
</div>