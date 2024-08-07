<%page 
    args="people"
/><!DOCTYPE html>
<html lang="en" translate="no" class="notranslate">
	<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta charset="utf-8"/>
		<meta name="google" content="notraslate"/>
        <style>
            
        </style>
    </head>
	<body class="notranslate">
        <ul> 
        % for person in sorted(people.values(),key=lambda p:f'{p.surname}, {p.given}'):
            % if person.surname: 
            <li>
                <a href="${person.id}/index.html">
                    ${person.surname}, ${person.given}, ${'?' if person.birthdate is None else person.birthdate.strftime("%Y")}
                </a>
                
            </li>
            % endif
        % endfor
        </ul>
    </body>
</html>
