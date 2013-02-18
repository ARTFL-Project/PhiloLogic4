<%namespace module="../philo_helpers" name="h" />

<%def name="make_cite(i, n)">    
    <%
    section_href = h.make_object_link(i.philo_id[:3], i.bytes)
    sub_section_href = h.make_object_link(i.philo_id[:4], i.bytes)
    para_href = h.make_object_link(i.philo_id[:5], i.bytes)
    section_names = i.headword.split(',')
    section_names = [i.div1.headword,i.div2.headword]
    if not section_names[0]:
        section_name = 'Article'
        sub_section_name = ''
        speaker_name = ''
    elif section_names[0].startswith('Dramatis'):
        section_name = section_names[0]
        sub_section_name = ''
        speaker_name = ''
    else:
        section_name = section_names[0]
        try:
            sub_section_name = section_names[1]
        except IndexError:
            sub_section_name = section_name
        speaker_name = i.who
    %>
    ${n}. <a href="${section_href}" class='philologic_cite'>${section_name}</a> 
    % if sub_section_name:
        - <a href="${sub_section_href}" class='philologic_cite'>${sub_section_name}</a> 
    % endif
        [${i.articleAuthor}]
        [${i.normalizedClass}]
    % if speaker_name:
        <a href="${para_href}" class='philologic_cite'>${speaker_name}</a>]
    % endif
        Tome ${i.volume}
</%def>