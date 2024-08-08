<%page 
    args="person,people,metadata"
/>
<%
displayed_metadata=[metadata[i] for i in person.metadata]
%><!DOCTYPE html>
<html lang="en" translate="no" class="notranslate">
	<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta charset="utf-8"/>
		<meta name="google" content="notraslate"/>
        <link rel="stylesheet" href="../static/styles.css">
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
            % for element in displayed_metadata:
            % if element["type"] == "picture":
            <div class="picture_element">

                <a name="${element["file"]}"/>
                <table WIDTH="600" Align="CENTER" NOBORDER COLS="2">
                    <tr>
                        <td ALIGN="CENTER" VALIGN="TOP">
                        <table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">
                            <tr>
                                <td ALIGN="CENTER" VALIGN="TOP">
                                    <H2>${element.get("title","")}</H2>
                                </td>
                            </tr>
                            <tr>
                                <td ALIGN="CENTER" VALIGN="TOP">
                                    <img src="${element["file"]}" target="Resource Window">
                                </td>
                            </tr>
                            <tr>
                                <td ALIGN="CENTER" VALIGN="TOP">
                                    <p>${element.get("caption","")}</p>
        <p><a href="mailto:pagerk@gmail.com?subject=${element["file"]}" target="_blank"><span style="font-size:xxx-large">&#x1f4e7;</span></a></p>
                                </td>
                            </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                
                <div class="ReturnToTop"><a href="#Top"><span style="font-size:xxx-large">&#x1F51D;</span></a></div>

              
                    </div>
            % endif
            % endfor
        </div>

    </body>
</html>
