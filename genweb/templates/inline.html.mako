<%page 
    args="element"
/><div class="inline_element">
    <a name="${element["file"]}"/>
    <H2  style="text-align:center;margin-left:auto;margin-right:auto;">${element.get("title", "Untitled")}</H2>
<p><a href="mailto:pagerk@gmail.com?subject=${element["file"]}" target="_blank"><span style="font-size:xxx-large">&#x1f4e7;</span></a></p>
    ${element.get("contents", "<b>content missing</b>")}
</div>
