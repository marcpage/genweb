<%page 
    args="element"
/><div class="picture_element">
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
                        <img src="../${element["path"]}/${element["file"]}" target="Resource Window">
                        % if "original" in element:
                        <a href="../${element["path"]}/${element["original"]}" target="Resource Window">
                        <font size="18"> &#x1F50D;</font>
                        </a>
                        % endif
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
