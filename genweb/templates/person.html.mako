<%page 
    args="person,people,metadata"
/>
<%
displayed_metadata=[metadata[i] for i in person.metadata]
displayed_metadata.sort(key=lambda e:e.get("file", ""))
years = sorted(set(e.get('file', "0000")[:4] for e in displayed_metadata))
%><!DOCTYPE html>
<html lang="en" translate="no" class="notranslate">
	<head>
        <title>${person.surname}, ${person.given}</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta charset="utf-8"/>
		<meta name="google" content="notraslate"/>
        <link rel="stylesheet" href="../static/styles.css">
        <script>
            <%include file="actions.js"/>
        </script>
    </head>
	<body class="notranslate">
        <div class="header">
            <div class="thumb"><img src="${person.id}.jpg" height=64 class="thumb_image"/></div>
            <h1>
                <a name="Top"></a>${person.surname}, ${person.given}
                - ${'?' if person.birthdate is None else person.birthdate.strftime("%Y")}
                - ${'?' if person.deathdate is None else person.deathdate.strftime("%Y")}
            </h1>
        </div>
        <div class="controls">
            <a href="../index.html">&#x1f3e0;</a>
        </div>

        <div class="nav_area">
            <%
            from datetime import date
            children = [i for i in person.children if i in people and people[i].metadata]
            children.sort(key=lambda i:people[i].birthdate if people[i].birthdate else date.today(), reverse=False)
            %>
            <%include file="nav_area.html.mako" args="people_ids=person.parents,people=people,area_class='parent_area',label='PARENTS'"/>
            <%include file="nav_area.html.mako" args="people_ids=person.spouses,people=people,area_class='spouse_area',label='SPOUSES'"/>
            <%include file="nav_area.html.mako" args="people_ids=sorted(children, key=lambda i:people[i].birthdate if birthdate else date.today()),people=people,area_class='child_area',label='CHILDREN'"/>

        </div>
        <div class="image_area">
            % for year in years:
                <span id="year-${year}-button" onclick="show_hide('year-${year}')" style="font-size:xx-large">▸</span>
                <span style="font-size:xxx-large" onclick="show_hide('year-${year}')">${year}</span>
                <div id="year-${year}" style="display:none">
                % for element in [e for e in displayed_metadata if e.get("file", "0000").startswith(year)]:
                % if element["type"] == "picture":
                    <%include file="picture.html.mako" args="element=element"/>
                % elif element["type"] == "inline":
                    <%include file="inline.html.mako" args="element=element"/>
                % elif element["type"] == "href":
                    <%include file="href.html.mako" args="element=element"/>

                % endif
                % endfor
                </div>
            % endfor
        </div>

    </body>
</html>
