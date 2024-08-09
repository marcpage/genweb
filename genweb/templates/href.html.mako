<%page 
    args="element"
/><div class="inline_element">

    <a name="${element["file"]}"/>
    <table WIDTH="600" Align="CENTER" NOBORDER COLS="1">
        <tr>
            <td ALIGN="CENTER" VALIGN="TOP">
                <table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">
                    <tr>
                        <td ALIGN="CENTER" VALIGN="TOP">
                            <H2>
                                <a href="../${element["path"]}/${element["folder"]}/${element["file"]}" target="_blank"><H2>${element["title"]}</H2></a>
                                <p><a href="mailto:pagerk@gmail.com?subject=${element["file"]}" target="_blank"><span style="font-size:xxx-large">&#x1f4e7;</span></a></p>
                            </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>

    <div class="ReturnToTop"><a href="#Top"><span style="font-size:xxx-large">&#x1F51D;</span></a></div>
</div>