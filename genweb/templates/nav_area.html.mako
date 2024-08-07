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
                <object data ="../${person}/${person}.jpg" type = "image/jpeg">
                    <img src = "../silhouette.jpg" />
                </object>
            </a>
        </div>
        % endif
    % endfor
</div>