<!DOCTYPE html PUBLIC"-//W3C//DTD HTML 4.01 Transitional//EN" >
<!-- Variables: people
 -->
<%
    current_letter = 'de' if people[0]['Surname'][0].startswith('de') else people[0]['Surname'][0]
%>
<html>
    <head>
		<meta charset="UTF-8">
        <title>Family History</title>
        <link href="css/index.css" type="text/css" rel="stylesheet">
        <link href="css/alphas.css" type="text/css" rel="stylesheet">
        <base target="right_frame">
    </head>
    <body background="images/back.gif">
        <table align="center" cellpadding="0" cellspacing="0" cols="2" width="75%" frame="border" rules="none">
            <tr>
                <td align="LEFT">
                    <img src="./images/HeaderPic.jpg" height="75">
                </td>
                <td align="LEFT">
                    <h2>Individual and Family Web Pages</h2>
                </td>
            </tr>
        </table>

        <table align="center" background="./images/back.gif" border cellpadding="8" cellspacing="4" cols="3">
            <tr>
                <td align="CENTER" valign="BOTTOM">
                    <p><a name='${current_letter}'><font size="+3" weight="900">${current_letter}</font></a></p>
                </td>

        % for person_index, person_facts in enumerate(people):
                <td align="CENTER" valign="BOTTOM">
                    <h5>${person_facts["Surname"]}, ${' '.join(person_facts["Given"])}
                    <a href= "${person_facts['long_genwebid']}/index.html"><img src="images/individual.bmp"></a>
                    <a href= "${person_facts['long_genwebid']}/HourGlass.html"><img src="images/family.bmp"></a>
            <%
                assert len(person_facts["BirthYear"]) in [0, 3, 4]
            %>
                    <br>${person_facts["BirthYear"] if person_facts["BirthYear"] else "?"} - ${person_facts["DeathYear"] if person_facts["DeathYear"] else "?"}</h5>
                </td>
            % if person_index % 3 == 1:
            </tr>
            <tr>
            % endif
        % endfor
            </tr>
        </table>
    </body>
</html>
