<%page 
    args="person,people"
/><!DOCTYPE html>
<html lang="en" translate="no" class="notranslate">
	<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta charset="utf-8"/>
		<meta name="google" content="notraslate"/>
        <style>
            .parent_area{
                background-color: azure;
                text-align: center;
            }
            .spouse_area{
                background-color: FloralWhite;
                text-align: center;
            }
            .child_area{
                background-color: lavender;
                text-align: center;
            }
            .person{
                background-color: white;
                display: inline-block;
                border: 1px solid white;
                border-radius: 15px;
                margin: 10px;
                text-align: center;
            }
            .label{
                height:100%;
                display:table-cell;
                vertical-align: middle;
                transform-origin:left;
                transform: rotate(-90deg) translate(-100%,10px);
                float: left;                
            }

            .controls{
                position:fixed;
                top:0;
                right:0;
            }
            
            h1 {
                text-align: center;
            }
        </style>
    </head>
	<body class="notranslate">
        <h1>
            <a name="Top"></a>${person.surname}, ${person.given}
             - ${'?' if person.birthdate is None else person.birthdate.strftime("%Y")}
             - ${'?' if person.deathdate is None else person.deathdate.strftime("%Y")}
        </h1>
        <div class="controls">
            <a href="../index.html">&#x1f3e0;</a>
        </div>

        <div class="nav_area">
            <%include file="nav_area.html.mako" args="people_ids = person.parents,people=people,area_class='parent_area',label='PARENTS'"/>
            <%include file="nav_area.html.mako" args="people_ids = person.spouses,people=people,area_class='spouse_area',label='SPOUSES'"/>
            <%include file="nav_area.html.mako" args="people_ids = person.children,people=people,area_class='child_area',label='CHILDREN'"/>

        </div>
        <div class="image_area">
        </div>

    </body>
</html>
