<%page 
    args="person,people"
/><!DOCTYPE html>
<html lang="en" translate="no" class="notranslate">
	<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta charset="utf-8"/>
		<meta name="google" content="notraslate"/>
    </head>
	<body class="notranslate">
        <h1>
            <a name="Top"></a>${person.surname}, ${person.given}
             - ${'?' if person.birthdate is None else person.birthdate.strftime("%Y")}
             - ${'?' if person.deathdate is None else person.deathdate.strftime("%Y")}
        </h1>

        <div class="nav_area">
            <%include file="nav_area.html.mako" args="people_ids = person.parents,people=people,area_class='parent_area'"/>
            <%include file="nav_area.html.mako" args="people_ids = person.spouses,people=people,area_class='spouse_area'"/>
            <%include file="nav_area.html.mako" args="people_ids = person.children,people=people,area_class='child_area'"/>

        </div>
        <div class="image_area">
        </div>

    </body>
</html>
