[![GitHub tag (latest SemVer)](https://img.shields.io/github/v/release/usgs/gems-tools-arcmap)](https://github.com/usgs/gems-tools-arcmap/releases/latest)
[![Wiki](https://img.shields.io/badge/-wiki-orange)](https://github.com/usgs/gems-tools-arcmap/wiki)
[![HTMLdoc](https://img.shields.io/badge/-jupyter_notebooks-orange)](https://github.com/usgs/gems-tools-pro/tree/notebooks)
[![ArcGISPro](https://img.shields.io/badge/-tools_for_arcgispro-orange)](https://github.com/usgs/gems-tools-pro) [![HTMLdoc](https://img.shields.io/badge/-online_gems_documentation-orange)](https://scgeology.github.io/GeMS/index.html) [![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/gems-schema/community) [![gems on USGS](https://img.shields.io/badge/-NGMDB_GeMS-brightgreen)](https://ngmdb.usgs.gov/Info/standards/GeMS/)

<img width="250" align="right" src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/USGS_logo_green.svg/500px-USGS_logo_green.svg.png"/>

# GeMS Tools for ArcMap

This repository contains an ArcGIS toolbox of Python 2.7 geoprocessing tools for creating, manipulating, and validating [GeMS](https://ngmdb.usgs.gov/Info/standards/GeMS/)-style geologic map databases for use in ArcMap. Additional resources; vocabularies, symbology, links to other projects, etc.; are available at the [NGMDB GeMS site](https://ngmdb.usgs.gov/Info/standards/GeMS/#reso).

If you are looking for tools that work in ArcGIS Pro, go to the [gems-tools-pro](https://github.com/usgs/gems-tools-pro) repository.

## Installation

* Download the [latest release](https://github.com/usgs/gems-tools-arcmap/releases/latest).
* Unzip the file to a folder of your choice. This will extract a single folder named `gems-tools-arcmap-` followed by the version number (e.g., `gems-tools-arcmap-1.2.2`).

* Start ArcCatalog or ArcMap
  * open the Arc Toolbox window
  * right-click on empty space in the Arc Toolbox window, and select "Add Toolbox".
  * navigate to the toolbox folder and select file **GeMSToolsArc105.tbx** (if you are running ArcGIS 10.5) or file **GeMSToolsArc10.tbx** (if you are running an older version of ArcGIS).
  * Right-click again on empty space in the Arc Toolbox window and select "Save settings" and then "Default" to have the GeMS toolbox available next time you open ArcCatalog or ArcMap.

or

* Place the **contents** of the toolbox folder (all sub-folders and files) in

    `C:\Documents and Settings\<user>\AppData\Roaming\ESRI\Desktop10.5\ArcToolbox\My Toolboxes`

    This is the pathname for ArcGIS 10.5 on Windows 7 and Windows 10; it may differ with other operating systems and ArcGIS versions. Delete the .tbx file that is not needed. Note that the AppData folder is hidden by default. To navigate to it in Windows Explorer, turn on Hidden items from the View tab. You can also open it by typing `%appdata%` in the run box, the search bar, or in the address bar of Windows Explorer
  * In ArcCatalog, scroll to the bottom of the left-hand "Catalog Tree" pane, open Toolboxes/My Toolboxes, and the new toolboxes should be present. You may need to refresh the listing.

## Getting Help

* Each tool comes with documentation inside the parameter form.
* Check out the [wiki](https://github.com/usgs/gems-tools-arcmap/wiki) for help on these tools and extensive advice on using these tools to create, edit, and validate GeMS-style databases.
* Documentation for the toolbox and all tools is also available in **GeMS_Tools_Arc10.docx** and **GeMS_Tools_Arc10.pdf** found in the `Docs` sub-folder.
* If, when using a tool, it fails to run and produces an error message, first check that you have the latest release of the tool. If that is not the source of the problem, start a new issue at this repository (see the [Issues](https://github.com/usgs/gems-tools-arcmap/issues) tab above). Provide a screenshot of the error message if you can.
* If you have a question about how to build or attribute a GeMS-compliant database or the schema in general, please visit the [GeMS Gitter](https://gitter.im/gems-schema/community#) chat room. If you already have a GitHub account, you can sign in there with those credentials.

## Collaboration
Suggestions for improvements and edited files submitted by [email](gems@usgs.gov) will be considered, but you are strongly encouraged to use GitHub to fork the project, create a new branch (e.g., "MyFixToProblemXXX"), make changes to this branch, and submit a pull request to have your changes merged with the master branch. Excellent guides for various aspects of the git workflow can be found here:

[https://guides.github.com/](https://guides.github.com/)

## Known issues
* "Project Map Data to Cross Section" doesn't always produce the correct apparent dip direction. The dip magnitude is correct, but it may be in the wrong direction.

* "MapOutline" stumbles over some choices of datum.

* ".docx to DMU" and "DMU to .docx" are incomplete and do not fully produce the desired output. These modules also
require the lxml Python module, which some find difficult to install. The other scripts run without lxml.  

* "Purge Metadata" requires that an older version of USGS EGIS tools for ArcGIS be installed.

## Acknowledgements
GeMS Tools was written in Python 2.7 by Ralph Haugerud, Evan Thoms, and others.

## Disclaimer
This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the U.S. Geological Survey (USGS). No warranty, expressed or implied, is made by the USGS or the U.S. Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the USGS nor the U.S. Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.

Any use of trade, firm, or product names is for descriptive purposes only and does not imply endorsement by the U.S. Government.
