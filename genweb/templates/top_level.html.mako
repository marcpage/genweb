<%page 
    args="people"
/><%
surnames = sorted(set(p.surname for p in people.values() if p.surname))
letters = sorted(set(s[0].upper() for s in surnames))
people_list = sorted(people.values(),key=lambda p:f'{p.surname}, {p.given}')
%><!DOCTYPE html>
<html lang="en" translate="no" class="notranslate">
	<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta charset="utf-8"/>
		<meta name="google" content="notraslate"/>
        <style>
            
        </style>
        <script>
        const closed = "▸";
        const open = "▾";
        function show_hide(identifier) {
            var div = document.getElementById(identifier);
            var button = document.getElementById(identifier+"-button");

            if (button.innerText == closed) {
                button.innerText = open;
                div.style.display = "block";
            } else {
                button.innerText = closed;
                div.style.display = "none";
            }
        }
        </script>
    </head>
	<body class="notranslate">
        % for letter in letters:
        <span id="letter-${letter}-button" onclick="show_hide('letter-${letter}')" style="font-size:xx-large">▸</span>
        <span style="font-size:xxx-large">${letter}</span>
        <div id="letter-${letter}" style="display:none">
            % for surname in [s for s in surnames if s[0].upper() == letter]:
            <span id="surname-${surname}-button" onclick="show_hide('surname-${surname}')" style="font-size:xx-large">▸</span>
            <span style="font-size:x-large">${surname}</span>
            <div id="surname-${surname}" style="display:none">
                <ul>
                    % for person in [p for p in people_list if p.surname == surname]:
                    <li>
                        <a href="${person.id}/index.html">
                            ${person.surname}, ${person.given}, ${'?' if person.birthdate is None else person.birthdate.strftime("%Y")}
                        </a>
                        
                    </li>
                    % endfor
                </ul>
            </div>
            <br/>
            % endfor
        </div>
        <br/>
        % endfor
    </body>
</html>
