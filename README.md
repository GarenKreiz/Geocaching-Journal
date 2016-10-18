# Geocaching-Journal
Generation of a journal of geocaching logs

## Features

* generation of XML files containing logs and list of pictures
* download a backup of the logs' web pages
* customization of HTML output with CSS styles or inside scripts
* require no external modules

This script works on Python 2.7.

## Usage

Save locally the content of the web page https://www.geocaching.com/my/logs.aspx?s=1 , for example in file geocaching_logs.html
Run the processLogs.py script to generate an XML file logbook.xml
It create a directory Logs to cache the logs' HTML page before parsing them.

```
$ python processLogs.py geocaching_logs.html logbook.xml
```

Check the content of the file : the title and description can be directly edited in the file or in processLogs.py 
Run the xml2print.py script to generate an HTML file

```
$ python xlp2print.py logbook.xml logbook.html
```

## Customization

In processLogs.py

* title of the output page
* description of the journal
* string to match to classify a picture as a panorama

In XML file

* insertion of new page markers <page/>

In xml2print.py

* numbers of columns for pictures

In logbook.css

* background images
* colors
* size and indentation

