<!DOCTYPE html PUBLIC"-//W3C//DTD HTML 4.01 Transitional//EN" >
<!-- Variables: family_dict, persons_xml_dict, admin_email, folders_path
 -->
<%
    import os

    table_col = 0
    long_genwebid = family_dict["target"]["long_genwebid"]
    personal_stories = long_genwebid == "StoriesPersonal0000-"

    if personal_stories:
        artifact_ids = sorted(persons_xml_dict["artifacts_info"], key=self._last)
    else:
        artifact_ids = sorted(persons_xml_dict["artifacts_info"])
%>
<html>
	<head>
		<meta charset="UTF-8">
		<title>Family History</title>
		<script type="text/javascript" src="../scripts/ImagePatch.js"></script>
		<link href="../css/individual.css" type="text/css" rel="stylesheet" />
		<style type="text/css">
		/*<![CDATA[*/
		div.ReturnToTop {text-align: right}
		/*]]>*/
		</style>
	</head>
	<body background="../images/back.gif" onload="patchUpImages()">
		<script>
		function playPauseVideo(identifier) {
			var myVideo = document.getElementById(identifier);
			if (myVideo.paused)
				myVideo.play();
			else
				myVideo.pause();
		}
		function setWidth(identifier, size) {
			var myVideo = document.getElementById(identifier);
			myVideo.width = size;
		}
		</script>

    % if personal_stories:
		<h1><a name="Top"></a>Personal Stories from our Ancestors</h1>
				<a href= "../../index.html"><img src="../images/Home.jpg"></a>
    % else:
		    <%
		        nickname = f'"{}"' if family_dict["target"]['Nickname'] else ''
		        birth_year = family_dict["target"]["BirthYear"]
		        birth_year = birth_year if len(birth_year) > 2 else "?"
		        death_year = family_dict["target"]["DeathYear"]
		        death_year = death_year if len(death_year) > 2 else "?"
		    %>
		<h1><a name="Top"></a>${family_dict["target"]["FullName"]}${nickname} - ${birth_year} - ${death_year}</h1>
		<a href= "HourGlass.html"><img src="../images/family.bmp"></a>
    % endif

    % if persons_xml_dict["artifacts_info"]:
		<!-- Index table -->
		<table align="center" border cellpadding="4" cellspacing="4" cols="3">
			<col width="33%">
			<col width="33%">
			<col width="33%">
			<tr>
        % for artifact_index, artifact in enumerate(artifact_ids):
				<td align="center" valign=top>
					<p><a href="#${os.path.basename(persons_xml_dict["artifacts_info"][artifact]["file"])}">${persons_xml_dict["artifacts_info"][artifact]["title"]}</a></p>
				</td>
            % if artifact_index % 3 == 2:
			</tr>
			<tr>
            % endif
        % endfor
            </tr>
		</table>
		<!-- Beginning of Content -->
		<!-- artifacts -->
		<p><em><strong>To identify people in a photograph:</em></strong></p>
		<ul>
		    <li><span style="font-size: 10pt">Click the smiley face next to the photo (the smiley face will change to a black checkmark).</span></li>
		    <li><span style="font-size: 10pt">Center the cross shaped cursor on the photograph and select the person</span></li>
		    <li style="margin-left:2em;font-size: 10pt">a dialogue box will open requesting the name of the person</li>
		    <li style="margin-left:2em;font-size: 10pt">continue selecting and naming people until you are done</li>
		    <li><span style="font-size: 10pt">Select the checkmark</span></li>
		    <li style="margin-left:2em;font-size: 10pt">your default email program will open with an email ready for you to send. </li>
		    <li><span style="font-size: 10pt">Send the email.</span></li>
		</ul>
    % for artifact_index, artifact in enumerate(artifact_ids):
        <%
            artifact_genwebid = artifact.lstrip("+0123456789")
            artifact_folder_path = os.path.join(folders_path, artifact_genwebid)
        %>

        % if persons_xml_dict["artifacts_info"][artifact]["tag_type"] == "picture":
		<a name="${os.path.basename(persons_xml_dict["artifacts_info"][artifact]["file"])}"/>
		<table WIDTH="600" Align="CENTER" NOBORDER COLS="2">
			<tr>
				<td ALIGN="CENTER" VALIGN="TOP">
				<table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">
					<tr>
						<td ALIGN="CENTER" VALIGN="TOP">
							<H2>${persons_xml_dict["artifacts_info"][artifact]["title"]}</H2>
						</td>
					</tr>
					<tr>
						<td ALIGN="CENTER" VALIGN="TOP">
							<img src="../${artifact_genwebid}/${artifact}.jpg" target="Resource Window">
                        % if os.path.isfile(f"${os.path.join(artifact_folder_path, f'+{artifact}.jpg')}"):
							<a href="../${artifact_genwebid}/+${artifact}.jpg" target="Resource Window">
                                <font size="18"> &#x1F50D;</font>
							</a>
                        % endif
						</td>
					</tr>
					<tr>
						<td ALIGN="CENTER" VALIGN="TOP">
					% if "caption" in persons_xml_dict["artifacts_info"][artifact]:
							<p>${persons_xml_dict["artifacts_info"][artifact]["caption"]}</p>
                            <p><a href="mailto:${admin_email}@gmail.com?subject=${artifact}" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a></p>
					% endif
						</td>
					</tr>
					</table>
				</td>
			</tr>
		</table>

		<div class="ReturnToTop"><a href="#Top"><font size="18"> &#x1F51D;</font></a></div>
        % endif

    % endfor





		<a name="${os.path.basename(persons_xml_dict["artifacts_info"][artifact]["file"])}"/>
            <H2 style="text-align:center;margin-left:auto;margin-right:auto;">Grandpa Reads - January 2004 &#x1F3A5;</H2>
            <p><a href="mailto:${admin_email}?subject=2004011500PageRobertK1949HughsMarillynM1925" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20">
        </a>
				<td align="center" valign=top>

        index_tbl_lines = []
        index_tbl_lines.append("
        index_tbl_lines.append(
		<table align="center" border cellpadding="4" cellspacing="4" cols="3">
        index_tbl_lines.append('			<col width="33%">
        index_tbl_lines.append('			<col width="33%">
        index_tbl_lines.append('			<col width="33%">

        artifacts_tbl_lines = []
        artifacts_tbl_lines.append("		<!-- Beginning of Content -->
        artifacts_tbl_lines.append("		<!-- artifacts -->
        artifacts_tbl_lines.append(
		<p><em><strong>To identify people in a photograph:</em></strong></p>"
        artifacts_tbl_lines.append("		<ul>")
        artifacts_tbl_lines.append(
		<li><span style="font-size: 10pt">Click the smiley face next to the photo (the smiley face will change to a black checkmark).</span></li>'
        artifacts_tbl_lines.append(
		<li><span style="font-size: 10pt">Center the cross shaped cursor on the photograph and select the person</span></li>'
        artifacts_tbl_lines.append(
		<li style="margin-left:2em;font-size: 10pt">a dialogue box will open requesting the name of the person</li>'
        artifacts_tbl_lines.append(
		<li style="margin-left:2em;font-size: 10pt">continue selecting and naming people until you are done</li>'
        artifacts_tbl_lines.append(
		<li><span style="font-size: 10pt">Select the checkmark</span></li>'
        artifacts_tbl_lines.append(
		<li style="margin-left:2em;font-size: 10pt">your default email program will open with an email ready for you to send. </li>'
        artifacts_tbl_lines.append(
		<li><span style="font-size: 10pt">Send the email.</span></li>'
        artifacts_tbl_lines.append("		</ul>")
        debug = False  # debug is set to False
        if long_genwebid == "":
            debug = True
        index_tbl_col = 1
        for artifact in artifact_ids:
            if artifact == "1917000000PageRaymondH1892HenryAnnaB1862":
                debug = False
            if artifact == "":
                print("artifact is = ", artifact)
            if debug:
                print("_generate_person_web line 734 artifact = ", artifact)
            artifact_genwebid = artifact.lstrip(
                "+0123456789"
            )  # this is the long genwebid
            artifact_folder_path = folders_path + "/" + artifact_genwebid
            # Generate index table
            if index_tbl_col == 1:
                index_tbl_lines.append("			<tr>

            index_tbl_lines.append('				<td align="center" valign=top>

            if debug:
                print(
                    "***************_generate_person_web line 1573: artifact = ",
                    artifact,
                        print("artifacts[artifact] = ", artifacts_info[artifact])
                print(
                    "sorted(artifacts_info[artifact].keys()) = ",
                    sorted(artifacts_info[artifact].keys()),
                        print(
                    "genwebid = ",
                    artifact_genwebid,
                    "   persons_xml_dict = ",
                    persons_xml_dict,
                    index_tbl_lines.append(
                '					<p><a href="#'
                + os.path.basename(persons_xml_dict["artifacts_info"][artifact]["file"])
                + '">'
                + persons_xml_dict["artifacts_info"][artifact]["title"]
                + "</a></p>
                index_tbl_lines.append("				</td>

            if index_tbl_col == 3:
                index_tbl_lines.append("			</tr>

            index_tbl_col = index_tbl_col + 1 if index_tbl_col < 3 else 1

            # Generate artifacts table
            if persons_xml_dict["artifacts_info"][artifact]["tag_type"] == "picture":
                artifacts_tbl_lines.append(
		<a name="'
                    + os.path.basename(
                        persons_xml_dict["artifacts_info"][artifact]["file"]
                                + '"/>
                        artifacts_tbl_lines.append(
		<table WIDTH="600" Align="CENTER" NOBORDER COLS="2">
                        artifacts_tbl_lines.append("			<tr>
                artifacts_tbl_lines.append('				<td ALIGN="CENTER" VALIGN="TOP">
                artifacts_tbl_lines.append(
				<table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">
                        artifacts_tbl_lines.append("					<tr>
                artifacts_tbl_lines.append(
						<td ALIGN="CENTER" VALIGN="TOP">
                        artifacts_tbl_lines.append(
                    "							<H2>"
                    + persons_xml_dict["artifacts_info"][artifact]["title"]
                    + "</H2>
                        artifacts_tbl_lines.append("						</td>
                artifacts_tbl_lines.append("					</tr>
                artifacts_tbl_lines.append("					<tr>
                artifacts_tbl_lines.append(
						<td ALIGN="CENTER" VALIGN="TOP">
                        # if  image doesn't exist, note it to be fixed
                if not os.path.isfile(
                    artifact_folder_path + "/" + artifact + ".jpg"
                ) and (long_genwebid in artifact):

                artifacts_tbl_lines.append(
							<img src="../'
                    + artifact_genwebid
                    + "/"
                    + artifact
                    + ".jpg"
                    + '" target="Resource Window">
                        if os.path.isfile(
                    artifact_folder_path + "/+" + artifact + ".jpg"
                ):  # if a hi res image exists, insert a link to it
                    artifacts_tbl_lines.append(
							<a href="../'
                        + artifact_genwebid
                        + "/+"
                        + artifact
                        + ".jpg"
                        + '" target="Resource Window">
                                # artifacts_tbl_lines.append('							<img src="../images/zoom.jpg' + '" target="Resource Window">
                    artifacts_tbl_lines.append(
							<font size="18"> &#x1F50D;</font>
                                artifacts_tbl_lines.append("							</a>
                artifacts_tbl_lines.append("						</td>
                artifacts_tbl_lines.append("					</tr>
                artifacts_tbl_lines.append("					<tr>
                artifacts_tbl_lines.append(
						<td ALIGN="CENTER" VALIGN="TOP">
                        if "caption" in persons_xml_dict["artifacts_info"][artifact]:
                    artifacts_tbl_lines.append(
                        "							<p>"
                        + persons_xml_dict["artifacts_info"][artifact]["caption"]
                        + f'</p>\n<p><a href="mailto:{self.admin_email}?subject='
                        + artifact
                        + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a></p>
                            else:
                    with open(
                        folders_path + "/zzz_Artifact_xml_issue.txt",
                        "a",
                        encoding="utf-8",
                    ) as debug_file:
                        debug_file.write(
                            "*****_generate_person_web caption Not Found in persons_xml_dict[artifacts_info][artifact] = "
                                        # debug_file.write(persons_xml_dict['artifacts_info'][artifact] + '

                artifacts_tbl_lines.append("						</td>
                artifacts_tbl_lines.append("					</tr>
                artifacts_tbl_lines.append("					</table>
                artifacts_tbl_lines.append("				</td>
                artifacts_tbl_lines.append("			</tr>
                artifacts_tbl_lines.append("		</table>
                artifacts_tbl_lines.append("
                # artifacts_tbl_lines.append('		<div class="ReturnToTop"><a href="#Top"><img src="../images/UP_DEF.GIF" border=0 /></a></div>
                artifacts_tbl_lines.append(
		<div class="ReturnToTop"><a href="#Top"><font size="18"> &#x1F51D;</font></a></div>
                        artifacts_tbl_lines.append("

            # some rejects proper_format = re.compile("[+]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9](([A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9])|[-])")
            # Works proper_format = re.compile("[+]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9][A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9]"
            # many rejects for no mother: proper_format = re.compile("[+]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9]")

            proper_format = re.compile(
                "[+]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9](([A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9])|[-])"
                if debug:
                format_match = str(proper_format.match(artifact))
            if debug:
                print(
                    " line 1645: proper_format.match(" + artifact + ")=" + format_match
                    if persons_xml_dict["artifacts_info"][artifact]["tag_type"] == "inline":
                if debug:
                    print(
                        "_generate_person_web line 1647: Now processing "
                        + artifact_folder_path
                        + "/"
                        + artifact
                        + ".src"
                            if os.path.isfile(
                    artifact_folder_path + "/" + artifact + ".src"
                ) and proper_format.match(
                    artifact
                ):  # if a src exists, insert it - continued
                    artifacts_tbl_lines.append(
		<a name="'
                        + os.path.basename(
                            persons_xml_dict["artifacts_info"][artifact]["file"]
                                        + '"/>
                                artifacts_tbl_lines.append(
		<H2  style="text-align:center;margin-left:auto;margin-right:auto;">'
                        + persons_xml_dict["artifacts_info"][artifact]["title"]
                        + f'</H2>\n<p><a href="mailto:{self.admin_email}?subject='
                        + artifact
                        + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>
                                artifacts_tbl_lines.append(
				<td align="center" valign=top>
                                artifacts_tbl_lines.append("
                    with open(
                        artifact_folder_path + "/" + artifact + ".src",
                        "r",
                        encoding="utf-8",
                    ) as artifact_source:
                        # print("line 1654 - " + artifact_folder_path + '/' + artifact + '.src') #Remove me
                        for line in artifact_source:
                            artifacts_tbl_lines.append(line)

                    artifacts_tbl_lines.append("
                    # artifacts_tbl_lines.append('		<div class="ReturnToTop"><a href="#Top"><img src="../images/UP_DEF.GIF" border=0 /></a></div>
                    artifacts_tbl_lines.append(
		<div class="ReturnToTop"><a href="#Top"><font size="18"> &#x1F51D;</font></a></div>
                                artifacts_tbl_lines.append("
                else:
                    with open(
                        folders_path + "/zzz_Artifact_xml_issue.txt",
                        "a",
                        encoding="utf-8",
                    ) as artifact_issue:
                        artifact_issue.write(
                            "*****BuildWebPages line 1655: "
                            + artifact_folder_path
                            + "/"
                            + artifact
                            + ".src file Not Found
                                        artifact_issue.write(
                            "*****BuildWebPages line 1656: artifact_folder_path = "
                            + artifact_folder_path
                            + "
                                        artifact_issue.write(
                            "*****BuildWebPages line 1657: artifact = "
                            + artifact
                            + "
                                        artifact_issue.write(
                            "*****BuildWebPages line 1658: persons_xml_dict[artifacts_info][artifact][file] = "
                            + persons_xml_dict["artifacts_info"][artifact]["file"]
                            + "
                                        artifact_issue.write(
                            "*****BuildWebPages line 1659: persons_xml_dict[artifacts_info][artifact][title] = "
                            + artifact
                            + "

                    if not proper_format.match(artifact):
                        with open(
                            folders_path + "/zzz_src_file_name_issue.txt",
                            "a",
                            encoding="utf-8",
                        ) as src_file_name_issue_file:
                            src_file_name_issue_file.write(
                                "*****_generate_person_web - inline: file name "
                                + artifact_folder_path
                                + "/"
                                + artifact
                                + ".src"
                                + " does not have the proper data format
                                        continue

            if persons_xml_dict["artifacts_info"][artifact]["tag_type"] == "href":
                if debug:
                    print(
                        "_generate_person_web line 834: persons_xml_dict[artifacts_info]["
                        + artifact
                        + "] = ",
                        persons_xml_dict["artifacts_info"][artifact],
                            html_path = (
                    artifact_folder_path
                    + "/"
                    + persons_xml_dict["artifacts_info"][artifact]["folder"]
                    + "/"
                    + persons_xml_dict["artifacts_info"][artifact]["file"]
                        if debug:
                    print(
                        "_generate_person_web line 836: Now processing href = ",
                        html_path,
                            if os.path.isfile(
                    artifact_folder_path
                    + "/"
                    + persons_xml_dict["artifacts_info"][artifact]["folder"]
                    + "/"
                    + persons_xml_dict["artifacts_info"][artifact]["file"]
                ):  # if an html exists, reference it - continued
                    artifacts_tbl_lines.append(
		<a name="'
                        + persons_xml_dict["artifacts_info"][artifact]["file"]
                        + '"/>
                                artifacts_tbl_lines.append(
		<table WIDTH="600" Align="CENTER" NOBORDER COLS="1">
                                artifacts_tbl_lines.append("			<tr>
                    artifacts_tbl_lines.append(
				<td ALIGN="CENTER" VALIGN="TOP">
                                artifacts_tbl_lines.append(
					<table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">
                                artifacts_tbl_lines.append("						<tr>
                    artifacts_tbl_lines.append(
							<td ALIGN="CENTER" VALIGN="TOP">
                                artifacts_tbl_lines.append("								<H2>
                    artifacts_tbl_lines.append(
									<a href="../'
                        + artifact_genwebid
                        + "/"
                        + persons_xml_dict["artifacts_info"][artifact]["folder"]
                        + "/"
                        + persons_xml_dict["artifacts_info"][artifact]["file"]
                        + '" target="_blank"><H2>'
                        + persons_xml_dict["artifacts_info"][artifact]["title"]
                        + f'</H2></a>\n<p><a href="mailto:{self.admin_email}?subject='
                        + artifact
                        + '" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>
                                artifacts_tbl_lines.append("							</td>
                    artifacts_tbl_lines.append("						</tr>
                    artifacts_tbl_lines.append("					</table>
                    artifacts_tbl_lines.append("				</td>
                    artifacts_tbl_lines.append("			</tr>
                    artifacts_tbl_lines.append("		</table>
                    artifacts_tbl_lines.append("
                    # artifacts_tbl_lines.append('		<div class="ReturnToTop"><a href="#Top"><img src="../images/UP_DEF.GIF" border=0 /></a></div>
                    artifacts_tbl_lines.append(
		<div class="ReturnToTop"><a href="#Top"><font size="18"> &#x1F51D;</font></a></div>
                                artifacts_tbl_lines.append("
                else:
                    with open(
                        folders_path + "/zzz_Artifact_xml_issue.txt",
                        "a",
                        encoding="utf-8",
                    ) as artifact_issue:
                        artifact_issue.write(
                            "*****BuildWebPages line 793: href file Not Found
                                        artifact_issue.write(
                            "*****BuildWebPages line 794:"
                            + artifact_folder_path
                            + "/"
                            + persons_xml_dict["artifacts_info"][artifact]["folder"]
                            + "/"
                            + persons_xml_dict["artifacts_info"][artifact]["file"]
                            + "

        index_tbl_lines.append("		</table>

        for line in index_tbl_lines:
            index_html_file.write(line)

        artifacts_tbl_lines.append("	</body>
        artifacts_tbl_lines.append("</html>

        for line in artifacts_tbl_lines:
            index_html_file.write(line)

        % endif
	</body>
</html>
