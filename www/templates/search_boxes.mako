<div class='form_body'>

<form id="search" action="${db.locals['db_url'] + "/dispatcher.py/"}">
<div id="report" class="report">
 <input type="radio" name="report" id="report1" value='concordance' checked="checked"><label for="report1">Concordance Report</label>
 <input type="radio" name="report" id="report2" value='relevance'><label for="report2">Ranked Relevance Report</label>
 <input type="radio" name="report" id="report4" value='collocation'><label for="report4">Collocation Table</label>
 <input type="radio" name="report" id="report5" value='frequency'><label for="report5">Frequency Table</label>
 <input type="radio" name="report" id="report6" value='time_series'><label for="report6">Time Series Report</label>
 </div>
 <div id="search_elements" class="search_elements">
 <table>
 <tr class="table_row" ><td class="first_column">Query Terms:</td><td class="second_column"><input type='text' name='q' id='q' class="search_box">
 </td></tr>
 <tr><td></td>
 <td><span id='method'>
 <input type="radio" name="method" id="method1" value='proxy' checked="checked"><label for="method1">Within</label>
 <input type='text' name='arg_proxy' id='arg_proxy' style="margin-left:15px !important;width:30px; text-align: center;">
 <span style="padding-left:5px;">words</span>
 <br><input type="radio" name="method" id="method2" value='phrase'><label for="method2">Exactly</label>
 <input type='text' name='arg_phrase' id='arg_phrase' style="margin-left:11px !important;width:30px; text-align: center;">
 <span style="padding-left:5px;">words</span>
 <br><input type="radio" name="method" id="method3" value='cooc'><label for="method3">In the same sentence</label>
 </span></td></tr>
% for facet in db.locals["metadata_fields"]:
    <tr id="metadata_field" class="table_row"><td class="first_column">${facet.title()}:</td><td><input type='text' name='${facet}' id="${facet}" class="search_box"></td></tr>
% endfor
 </table>
<table> 
 <tr class="table_row" id="collocation"><td class="first_column">Within </td><td><span id='word_num'>
 <input type="radio" name="word_num" id="wordnum1" value="1"><label for="wordnum1">1</label>
 <input type="radio" name="word_num" id="wordnum2" value="2"><label for="wordnum2">2</label>
 <input type="radio" name="word_num" id="wordnum3" value="3"><label for="wordnum3">3</label>
 <input type="radio" name="word_num" id="wordnum4" value="4"><label for="wordnum4">4</label>
 <input type="radio" name="word_num" id="wordnum5" value="5" checked="checked"><label for="wordnum5">5</label>
 <input type="radio" name="word_num" id="wordnum6" value='6'><label for="wordnum6">6</label>
 <input type="radio" name="word_num" id="wordnum7" value='7'><label for="wordnum7">7</label>
 <input type="radio" name="word_num" id="wordnum8" value='8'><label for="wordnum8">8</label>
 <input type="radio" name="word_num" id="wordnum9" value="9"><label for="wordnum9">9</label>
 <input type="radio" name="word_num" id="wordnum10" value="10"><label for="wordnum10">10</label>
 </span> words</td></tr>

 
 <tr class="table_row" id="frequency"><td class="first_column">Frequency by:</td><td><span id='field'>
% for pos, facet in enumerate(db.locals["metadata_fields"]):
    % if pos == 0:
        <input type="radio" name="field" id="field${pos}" value='${facet}' checked='checked'><label for="field${pos}">${facet}</label>
    % else:
        <input type="radio" name="field" id="field${pos}" value='${facet}'><label for="field${pos}">${facet}</label>
    % endif
% endfor
</span>
<input type="checkbox" name="rate" id="rate" value="relative"/>per 10,000 words
</td></tr>

<tr class="table_row" id="time_series">
<td class="first_column">Dates:</td><td>from <input type='text' name="start_date" id="start_date" style="width:35px;"> to <input type='text' name="end_date" id="end_date" style="width:35px;">
<tr class="table_row" id="year_interval"><td class="first_column">Year interval:</td><td><span id="year_interval">
<input type="radio" name="year_interval" id="year0" value="1" checked="checked"><label for="year0">every year</label>
<input type="radio" name="year_interval" id="year1" value="10" checked="checked"><label for="year1">every 10 years</label>
<input type="radio" name="year_interval" id="year2" value="25"><label for="year2">every 25 years</label>
</span>
</td></tr>

<tr class="table_row" id="results_per_page"><td class="first_column">Results per page:</td><td><span id='page_num'>
 <input type="radio" name="pagenum" id="pagenum1" value='20' checked="checked"><label for="pagenum1">20</label>
 <input type="radio" name="pagenum" id="pagenum2" value='50'><label for="pagenum2">50</label>
 <input type="radio" name="pagenum" id="pagenum3" value='100'><label for="pagenum3">100</label>
 </span></td></tr>
 <tr class="table_row"><td class="first_column"><input id="button" type='submit' value="Search"/></td>
 <td><button type="reset" id="reset">Clear form</button></td></tr>
</table>
</div>
</form>
<div id="form_separation" class="form_separation">
<a href="javascript:void(0)" class="show_search_form" id="show_search_form" title="Click to show the search form">Show search parameters</a>
</div>
</div>
<div id="waiting" style="display:none;z-index:99;position:absolute;"><img src="http://pantagruel.ci.uchicago.edu/philo4/Frantext_clovis/js/ajax-loader.gif" alt="Loading..."/></div>