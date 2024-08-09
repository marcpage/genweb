<%page 
    args="people_ids,people,area_class,label"
/><%
display_people = [p for p in people_ids if p in people and people[p].metadata]
%>
% if display_people: 
<div class="${area_class}">
    <div class="label">${label}</div>

    % for person in display_people:
        <div class="person">
           <a href="../${person}/index.html"> 
                <img src = "../${person}/${person}.jpg" height=64 class="thumb_image"/>
                <br/>
                ${people[person].given.split(" ")[0]}
            </a>
        </div>
    % endfor
</div>
% endif