<!DOCTYPE html PUBLIC"-//W3C//DTD HTML 4.01 Transitional//EN" >
<!-- Variables: current_letter, person_facts, target_person
 -->
<%
    table_col = 0
%>
<html>
    <head>
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

        <table align="center" background="./images/back.gif" border cellpadding="8" cellspacing="4" cols="3">\n'
            <tr>
            <%
                table_col = table_col + 1
            %>
                <td align="CENTER" valign="BOTTOM">
                    <p><a name='${current_letter}'><font size="+3" weight="900">${current_letter}</font></a></p>
                </td>
            <%
                table_col = table_col + 1
            %>
                <td align="CENTER" valign="BOTTOM">
                    <h5>${person_facts["Surname"]}, ${' '.join(person_facts["Given"])}
                    <a href= "${target_person}/index.html"><img src="images/individual.bmp"></a>
                    <a href= "${target_person}/HourGlass.html"><img src="images/family.bmp"></a>
            <%
                assert len(person_facts["BirthYear"]) in [0, 3, 4]
            %>
                    <br>${person_facts["BirthYear"] if person_facts["BirthYear"] else "?"} - {person_facts["DeathYear"] if person_facts["DeathYear"] else "?"}</h5></p>
                </td>

                if current_letter == previous_letter:
                    table_col = table_col + 1
        \t\t<td align="CENTER" valign="BOTTOM">
                    full_given = ""
                    if debug:
                        print("_generate_toc_web line 718 person_facts = ", person_facts)

                    for given_no in range(len(person_facts["Given"])):
                        given = person_facts["Given"][given_no]
                        full_given = full_given + " " + given

                        "\t\t\t\t\t<h5>"
                        + person_facts["Surname"]
                        + ", "
                        + full_given
                        + "\n"
                    )
                    if debug:
                        print("******* _generate_toc_web line 724 person = ", person)

\t\t\t\t<a href= "./'
                        + target_person
                        + '/index.html"><img src="./images/individual.bmp"></a>\n'
                    )

\t\t\t\t<a href= "./'
                        + target_person
                        + '/HourGlass.html"><img src="./images/family.bmp"></a>\n'
                    )
                    birth_year = (
                        person_facts["BirthYear"]
                        if len(person_facts["BirthYear"]) > 2
                        else "?"
                    )
                    death_year = (
                        person_facts["DeathYear"]
                        if len(person_facts["DeathYear"]) > 2
                        else "?"
                    )

                        "\t\t\t\t\t\t<br>" + birth_year + " - " + death_year + "</h5></p>\n"
                    )
                    "\t\t\t\t</td>

                if table_col == 3:
                    "\t\t\t</tr>
                    "\t\t\t<tr>
                    table_col = 0
                previous_letter = current_letter
