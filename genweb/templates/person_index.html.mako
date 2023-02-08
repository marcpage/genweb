<!DOCTYPE html PUBLIC"-//W3C//DTD HTML 4.01 Transitional//EN" >
<!-- Variables: family_dict, persons_xml_dict, admin_email, folders_path
 -->
<%
    import os
    import re

    table_col = 0
    long_genwebid = family_dict["target"]["long_genwebid"]
    personal_stories = long_genwebid == "StoriesPersonal0000-"

    if personal_stories:
        artifact_ids = sorted(persons_xml_dict["artifacts_info"], key=self._last)
    else:
        artifact_ids = sorted(persons_xml_dict["artifacts_info"])

    proper_format = re.compile(
        "[+]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9](([A-Za-z']+[A-Z][a-z]*[0-9][0-9][0-9][0-9])|[-])"
    )
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
        % endif


        % if persons_xml_dict["artifacts_info"][artifact]["tag_type"] == "inline":
            <%
                source_file = os.path.join(artifact_folder_path, artifact + ".src")
            %>
		    % if os.path.isfile(source_file) and proper_format.match(artifact):
            <%
                with open(source_file, 'r', encoding='utf-8') as source_file:
                    contents = source_file.read()
            %>
		<a name="${os.path.basename(persons_xml_dict["artifacts_info"][artifact]["file"])}"/>
		<H2  style="text-align:center;margin-left:auto;margin-right:auto;">${persons_xml_dict["artifacts_info"][artifact]["title"]}</H2>
        <p><a href="mailto:${admin_email}?subject=${artifact}" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>
        ${contents}
		    % endif
        % endif


        % if persons_xml_dict["artifacts_info"][artifact]["tag_type"] == "href":
            <%
                linked_folder = persons_xml_dict["artifacts_info"][artifact]["folder"]
                linked_file = persons_xml_dict["artifacts_info"][artifact]["file"]
            %>
            % if os.path.isfile(os.path.join(artifact_folder_path, linked_folder, linked_file)):

		<a name="${os.path.basename(persons_xml_dict["artifacts_info"][artifact]["file"])}"/>
		<table WIDTH="600" Align="CENTER" NOBORDER COLS="1">
			<tr>
				<td ALIGN="CENTER" VALIGN="TOP">
					<table Align=CENTER BORDER CELLPADDING="4" CELLSPACING="4" COLS="1">
						<tr>
							<td ALIGN="CENTER" VALIGN="TOP">
								<H2>
								<a href="../${artifact_genwebid}/${persons_xml_dict["artifacts_info"][artifact]["folder"]}/${persons_xml_dict["artifacts_info"][artifact]["file"]}" target="_blank">
								    <H2>${persons_xml_dict["artifacts_info"][artifact]["title"]}</H2>
								</a>
                                <p><a href="mailto:${admin_email}?subject=${artifact}" target="_blank"><img alt="comments" src="../images/comments.jpg" style="display: block; text-align: center; margin-left: auto; margin-right: auto" height="20"></a>
							</td>
						</tr>
					</table>
				</td>
			</tr>
		</table>

            % endif
        % endif


		<div class="ReturnToTop"><a href="#Top"><font size="18"> &#x1F51D;</font></a></div>
    % endfor
% endif
	</body>
</html>
