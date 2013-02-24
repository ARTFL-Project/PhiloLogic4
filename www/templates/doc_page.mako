<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<div class='philologic_response'>
 <p class='description' style="width:0% !important;margin-left:auto;margin-right:auto;">${current_page}</p>
 <div class='page_display' style='clear:both;'>
 ${page_text}
</div>
<div class="more">
<table><tr>
<td><a href="?report=pagination&philo_id=${philo_id}&doc_page=${prev_page}&filename=${filename}&byte=${'&byte='.join(bytes.split('+'))}">Previous</a></td>
<td><a href="?report=pagination&philo_id=${philo_id}&doc_page=${next_page}&filename=${filename}&byte=${'&byte='.join(bytes.split('+'))}">Next</a></td>
</tr></table>
<div style='clear:both;'></div>
</div>
</div>
<%include file="footer.mako"/>
