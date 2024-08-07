<%page 
    args="person"
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
            <div class="parent_area">
                % for parent in person.parents:
                    <div class="person">
                       <a href="../${parent}/index.html"> <img src="../${parent}/${parent}.jpg"/></a>
                    </div>

                % endfor
            </div>
            <div class="spouse_area">

                % for spouse in person.spouses:
                    <div class="person">
                       <a href="../${spouse}/index.html"> <img src="../${spouse}/${spouse}.jpg"/></a>
                    </div>
                % endfor

            </div>
            <div class="child_area">

                % for child in person.children:
                    <div class="person">
                       <a href="../${child}/index.html"> <img src="../${child}/${child}.jpg"/></a>
                    </div>
                % endfor
                
            </div>
        </div>
        <div class="image_area">
        </div>

    </body>
</html>
