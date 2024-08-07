<%page 
    args="people_ids,people,area_class"
/><div class="${area_class}">
    % for person in people_ids:
    <%
    is_linkable = person in people and people[person].metadata
    %>
        % if is_linkable:
        <div class="person">
           <a href="../${person}/index.html"> 
                <img src="../${person}/${person}.jpg"/>
            </a>
        </div>
        % endif
    % endfor
</div>