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
                <object data ="../${person}/${person}.jpg" type = "image/jpeg" height=64>
                    <img src = "../silhouette.jpg" height=64/>
                </object>
                <br/>
                ${people[person].given.split(" ")[0]}
            </a>
        </div>
        % endif
    % endfor
</div>