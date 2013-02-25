<%include file="header.mako"/>
<div class="back_to_contents"><a href="${philo_id}">Back to table of contents</a></div>
<div class='philologic_response'>
 <p class='description' style="width:5% !important;margin-left:auto;margin-right:auto;">${current_page}</p>
 <div class='page_display' style='clear:both;'>
 ${page_text}
</div>
<div class="doc_pages">
<table><tr>
<td><a href="?report=pagination&philo_id=${philo_id}&doc_page=${prev_page}&filename=${filename}" class="prev_next"><</a></td>
<td><a href="?report=pagination&philo_id=${philo_id}&doc_page=${next_page}&filename=${filename}" class="prev_next">></a></td>
</tr></table>
<div style='clear:both;'></div>
</div>
</div>
<%include file="footer.mako"/>
