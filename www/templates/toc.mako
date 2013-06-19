<% results = navigate_doc(obj, db) %>
<div id="table_of_contents" class="table_of_contents" style='display:block;'>
    % for i in results:
        <% 
        id = i.philo_id[:7]
        href = f.link.make_absolute_object_link(db,id)
        if i.type == "div2":
            spacing = "&nbsp;-&nbsp;"
        elif i.type == "div3":
            spacing = "&nbsp;&nbsp;&nbsp;-&nbsp;"       
        else:
            spacing = ""
        %>
        ${spacing}<a href="${href}">${i.head or "[%s]" % i.type}</a><br>
    % endfor
</div>