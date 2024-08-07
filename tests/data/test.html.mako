<%page 
    args="color, name"
/><!DOCTYPE html>
<html lang="en" translate="no" class="notranslate">
	<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta charset="utf-8"/>
		<meta name="google" content="notraslate"/>
    </head>
	<body class="notranslate">
        <%include file="test_include.html.mako" args="name=name"/>
        color=${color}
    </body>
</html>
