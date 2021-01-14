#!python
# -*- coding: utf-8 -*-
"""
################################################################################
# xml2print.py
#
#     transforms an XML description of a logbook or blog into HTML
#     generates a random mosaic of a small sqare version of all pictures
#     allow the selection of some pictures
#
#     tags : title, description, date, post, text, image, pano
#
# Copyright GarenKreiz at  geocaching.com or on  YouTube 2010-2018
# Auteur    GarenKreiz sur geocaching.com ou sur YouTube
#
# Licence:
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""

import re
import sys
import codecs
import string

maxRow = 3   # number of pictures in a row (less than 4)
allPictures = {};  # all picture descriptions

# HTML templates to generate the web page

headerStart = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta content="IE=EmulateIE7" http-equiv="X-UA-Compatible">
<meta content="true" name="MSSmartTagsPreventParsing">
<link rel="stylesheet" type="text/css" href="logbook.css" media="all">
<!-- Generated by xml2print.py from Garenkreiz -->
"""

headerMiddle = """
</head>
<body>
<div class="header">
<h1>%s</h1>
"""

headerEnd = """
<p class="description"><i>%s</i></p>
</div> <!-- header -->
<div class="main">
"""

dateFormat = '<div class="date"><h2 class="date-header">%s</h2><div class="post-entry">'
postBegin = '<h3 class="post-title">'
postMiddle = '</h3>'
postBanner = '<div class="post-banner"></div><div class="post-entry">'
postEnd = '</div>'
dateEnd = '</div>  <!--// class:date //-->'

pictureFormatTemplate = """
<table class="picture"><tbody>
<tr><td><img class="%s" src="%s"/></td></tr>
<tr><td class="caption">%s</td></tr>
</tbody></table>
"""

# file from http://www.geocaching.com/app/ui-icons/sprites/cache-types.svg (Copyright Groundspeak)
iconBadgeTemplate = '<svg class="post-badge"><use xlink:href="./cache-types.svg#icon-%s" /></svg>'
iconPostTemplate = '<svg class="post-icon"><use xlink:href="./cache-types.svg#icon-%d" /></svg>'

# file from http://www.geocaching.com/images/icons/fave_fill_16.svg (Copyright Groundspeak)
iconFavoriteTemplate = '<svg width="16px" height="16px"><image xlink:href="./fave_fill_16.svg" /></svg>'

headerMosaic = """
<style>
.thumb {
    display: inline-block;
    width: 80px;
    height: 80px;
    margin: 0px;
    border: 1px solid #000000;
    background-position: center center;
    background-size: cover;
    margin:0px;outline:none;
    vertical-align: top;
    padding: 0px;
    object-fit: cover;
    }
</style>
"""

headerPopup="""
<script language="JavaScript">
<!--

var currentPictureUrl;
var currentPictureName;
var currentCacheUrl;
var currentLogUrl;
var currentCacheName;

function downloadSelection() {
    var filename = 'selectionImages.html';
    var element = document.createElement('a');
    var text = "<html><head>";
    text += document.getElementsByTagName('head')[0].innerHTML;
    text += "</head><body>";
    text += document.getElementById('selectionBody').innerHTML;
    text += "</body></html>";

    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
};

function selectPicture()
{
    var text = document.getElementById('selectionBody').innerHTML;
    if (text == '')
    {
       text = '<h2 class="date-header">Selection Images</h2>';
    };
    text += '<div class="post-banner"></div><div class="post-entry">';
    text += '<h3 class="post-title">';
    text += '<div class="alignleft"><a href="'+ currentCacheUrl + '" target="_blank">' + currentCacheName + '</a></div>';
    text += '<div class="alignright"><a href="'+ currentLogUrl + '" target="_blank">' + 'Log' + '</a></div>';
    text += '</h3><br />';
    text += '<h3 class="post-title" align="middle">' + currentPictureName + '<br />';
    text += '<img align="middle" style="max-width: 100%;" src="' + currentPictureUrl + '"></div></h3></div>';
    document.getElementById('selectionBody').innerHTML = text;
    document.getElementById('selectionLayer').style.visibility = "visible";
    closePopImage();
};

function showPopup(id, state) 
{
    var obj = document.getElementById(id);
    obj.style.visibility = state ? "visible" : "hidden";
};

function popImage(url,name,cacheUrl,logUrl,cacheName)
{
    currentPictureUrl = url;
    currentPictureName = name;
    currentCacheUrl = cacheUrl;
    currentLogUrl = logUrl
    currentCacheName = cacheName;
    currenLogUrl = logUrl;
    var image = document.getElementById('popupContent').getElementsByTagName('img')[0];
    image.src = url;
    document.getElementById('popupTitle').innerHTML = "&nbsp;&nbsp;"+name;
    document.getElementById('showCache'    ).setAttribute("onclick","window.open('" + cacheUrl + "', '_blank');");
    document.getElementById('showLog'      ).setAttribute("onclick","window.open('" + logUrl + "', '_blank');");
    document.getElementById('selectPicture').setAttribute("onclick","selectPicture();");
    showPopup('popupButtons',1);
    showPopup('popupLayer',1);
};

function closePopImage()
{
    var image = document.getElementById('popupContent').getElementsByTagName('img')[0];
    image.src = "";
    showPopup('popupLayer',0);
    showPopup('popupButtons',0);
};

// -->
</script>
"""
    
bodyMosaic="""
</head>
<body>
"""

htmlEnd="""
<!-- Popup Layer -->
<div id="popupLayer">
  <div id="popupWindow">
    <div id="popupBar">
        <div id="popupClose" >
            <a href="javascript:void(0);"
               onClick="closePopImage();return false" >
               X</a>
        </div>
        <div>&nbsp</div>
        <div id="popupTitle"> TITRE </div>
    </div>
    <div id="popupContent">
      <img id="popupImage" src="">
    </div>
    <div id="popupButtons">
      <input type="button" id="showLog"   value="Log"   onclick="window.open('', '_blank');"  >
      <input type="button" id="showCache" value="Cache" onclick="window.open('', '_blank');"  >
      <input type="button" id="selectPicture" value="Select" onclick="window.open('', '_blank');"  >
    </div>
  </div>
</div>
<!-- End Popup layer -->
<!-- Console Layer -->
<div id="selectionLayer" style="visibility:hidden;">
  <p></p>
  <button onclick="downloadSelection();">Save</button>
  <p></p>
  <div id="selectionBody"></div>
</div>
<!-- End Console layer -->
<!-- Template for selected image -->
<div id="selectedImageTemplate" style="visibility:hidden;">
  <div class="post-banner"></div>
  <div class="post-entry">
    <h3 class="post-title">
      <div class="alignleft"><a href="" target="_blank">Cache</a></div>
      <div class="alignright"><a href="" target="_blank">Log</a></div>
    </h3>
    <h3 class="post-title"><br><img src="" align="middle"></h3>
  </div>
</div>
<!-- End Template for selected image -->
</body></html>
"""


def safeString(s):
    """
    process single and double quotes
    """
    s = re.sub('\'','\&apos;',s)
    s = re.sub('&#39;','\&apos;',s)
    return re.sub('\"','\&quot;',s)


def cleanText(textInput, allTags=True):
    """
    cleaning text from HTML formatting
    """
    resu = re.sub('</*(tbody|table|div|text)[ /]*>', ' ', textInput)
    resu = re.sub('</*div>'                        , '',  resu)
    resu = re.sub('<div[^>]*>'                     , '',  resu)
    resu = re.sub('[\n\r]*'                        , '',  resu)
    # geocaching emoticons
    resu = re.sub('img src="/images/icons','img src="https://www.geocaching.com/images/icons', resu)
    if allTags:
        resu = re.sub('<[^>]*>', '', resu)
    return resu


def flushGallery(fOut, pictures, groupPanoramas=False, compactGallery=False):
    """
    print(the image gallery of a post, possibly grouping all panoramas at the end)
    """

    if groupPanoramas:
        panoramas = []
        plainPictures = []
        for (format, image, comment, width, height) in pictures:
            if format == 'panorama':
                panoramas.append((format, image, comment, width, height))
            else:
                plainPictures.append((format, image, comment, width, height))
        flushSubGallery(fOut,plainPictures,compactGallery)
        flushSubGallery(fOut,panoramas, compactGallery=False)
    else:
        flushSubGallery(fOut,pictures, compactGallery=False)


def flushSubGallery(fOut, pictures, compactGallery=False):
    """
    print(a sub gallery of images in sequence)
    """

    if pictures == []:
        return
    
    rowCount = 0       # current number of images in row
    panoramas = []

    if compactGallery and len(pictures) % 3 > 0:
        # Starting with a row of 2 pictures
        rowCount = 1
    fOut.write('<table class="table-pictures"><tr>\n')
    for (format, image, comment, width, height) in pictures:
        comment = re.sub('&pad;', '', comment)
        if format == 'panorama' and rowCount > 0 or rowCount == maxRow:
            # start a new row of pictures
            fOut.write('</tr></table>\n')
            fOut.write('<table class="table-pictures"><tr>\n')
            rowCount = 0
        rowCount = (maxRow if format == 'panorama' else rowCount + 1)
        fOut.write('<td>')

        # specific to geocaching logs : open a full sized view of picture
        imageFullSize = re.sub('https://img.geocaching.com/cache/log/display/', 'https://img.geocaching.com/cache/log/', image)
        (comment, location, url1, url2, cacheName) = allPictures[image][-1]
        popupLink = '<a href="javascript:void(0)" onclick="javascript:popImage(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\');">'%(imageFullSize,safeString(comment), url1, url2, safeString(cacheName))
        fOut.write(popupLink + pictureFormatTemplate % (format, image, comment) + '</a>')
        comment = re.sub('<br>', '', comment)
        fOut.write('</td>\n')
    fOut.write('</tr></table>\n')


def flushText(fOut,text):
    """
    flushing text as HTML paragraph
    """

    if text:
        if '<p>' not in text[0:10]:
            text = '<p>'+text+'</p>'
        fOut.write(text)

typeIcons = {
    'Traditional Cache' : 2,
    'Multi-cache'       : 3,
    'Virtual Cache'     : 4,
    'Letterbox Hybrid'  : 5,
    'Event Cache'       : 6,
    'Mystery Cache'     : 8,
    'Unknown Cache'     : 8,
    'Project APE Cache' : 9,
    'Webcam Cache'      : 11,
    'Locationless (Reverse) Cache' : 12,
    'Cache In Trash Out Event' : 13,
    'Earthcache'        : 137,
    'Mega-Event'        : 453,
    'Wherigo Cache' : 1858,
    'Community Celebration Event' : 3653,
    'Geocaching HQ' : 3773,
    'Giga-Event'    : 7005,

    'Found it' : 'found',
    'Didn\'t find it' : 'dnf',
    'Write note' : 'cachenote',
    'Will Attend' : 'found-disabled',
    'Attended' : 'found',
    'Temporarily Disable Listing' : 'draft-disabled',
    'Owner Maintenance' : 'owned',
    'Enable Listing' : 'generic',
    'Webcam Photo Taken' : 'found',
    }

def xml2print(xmlInput, htmlOutput, printing=False, groupPanoramas=False, compactGallery=False, mosaic=None, icons=False):
    """
    main function of module : generation of an HTML file from an XML file
    """

    global typeIcons
    
    #fOut = open(htmlOutput, 'w', encoding="utf-8")
    fOut = codecs.open(htmlOutput, 'w', 'utf-8')
    firstDate = True
    pictures = []
    processingPost = False
    text = ''
    elements = []
    log = None
    preformatted = False

    fOut.write(headerStart)

    print("Processing", xmlInput)
    # f = open(xmlInput, 'r')
    f = codecs.open(xmlInput, 'r', 'utf-8')
    currentLocation = ''
    currentURL = ''
    currentAdditionalURL = ''
    
    # process each item of the XML input file
    l = f.readline()
    while l != '':
        # analyse of the XML tag
        tag = re.sub('>.*', '>', l.strip())

        if tag in ['<image>','<pano>','<post>','<date>','</text>']:
            flushText(fOut,text)
            text = ''
        if tag not in ['<image>', '<pano>']:
            flushGallery(fOut,pictures,groupPanoramas,compactGallery)
            pictures = []
            
        if tag == '<image>' or tag == '<pano>':
            # parsing image item
            # <image>foo.jpg<height>480</height><width>640</width><comment>Nice picture</comment></image>
            # <pano>foo.jpg<height>480</height><width>1000</width><comment>Nice panorama</comment></image>
            # displaying images in tables
            line = re.sub('<[^>]*>', '|', l)
            try:
                imgDesc = line.split('|')
            except Exception as msg:
                print('!!!!!!!!!!!!! Exception: bad image format:', msg, line)
            if len(imgDesc) == 4:
                (_, image, comment, _) = imgDesc
            elif len(imgDesc) == 9:
                (_, image, height, _, width, _, comment, _, _) = imgDesc
            else:
                print('!!!!!!!!!!!!! Bad image format:', line)
            try:
                allPictures[image].append((comment,currentLocation,currentURL,currentAdditionalURL,elements[0]))
                print("Image en double :", image, currentLocaltion, currentURL)
            except:
                allPictures[image] = [(comment,currentLocation,currentURL,currentAdditionalURL,elements[0])]
            if tag == '<pano>':
                pictures.append(('panorama', image, comment, width, height))
            elif height > width:
                pictures.append(('portrait', image, comment, width, height))
            else:
                pictures.append(('landscape', image, comment, width, height))

        elif tag == '<title>':
            # title of the logbook
            l = re.sub('</*title>', '', l)
            title = l.split('|')
            fOut.write('<title>%s</title>\n' % cleanText(title[0], True))
            if len(title) == 2:
                # the title has 2 parts : a text | an URL
                titleText = '<a href="%s" target="_blank">%s</a>' % (title[1], title[0])
            else:
                fOut.write('<title>%s</title>\n' % cleanText(l, True))
                titleText = title[0]
            fOut.write(headerPopup)
            fOut.write(headerMiddle % titleText)

        elif tag == '<description>':
            # description of the logbook
            fOut.write(headerEnd % cleanText(l))

        elif tag == '<date>':
            # new date in the logbook
            if firstDate is False:
                fOut.write(postEnd + dateEnd)
            firstDate = False
            processingPost = False

            date = cleanText(l)
            if date != '':
                #date = string.upper(date[0])+date[1:]
                date.capitalize()
            fOut.write(dateFormat % date)
            text = ''

        elif tag == '<post>':
            # new post title : left text | url | right text | url
            if processingPost:
                fOut.write(postEnd + postBanner) # banner between 2 posts
            processingPost = True
            post = cleanText(l)
            try:
                print('Post:', re.sub('\|.*', '', post))
            except:
                print('Post:', (re.sub('\|.*', '', post)).encode('utf-8'))

            # <post>left title|left url|right title|right url</post>
            elements = post.split('|')
            post = elements[0].strip()
            if len(elements) > 1:
                currentLocation = elements[0].strip()
                currentURL = elements[1]
                currentAdditionalURL = ''
                post = '<a href="' + elements[1] + '" target="_blank">' + post + '</a>'
                log = ''
                if len(elements) > 2:
                    log = elements[2].strip()
                    if 'geocaching' in currentURL:
                        favorite = ''
                        types = re.search('([^\[]*)(\[[^\[]*\])?$', log)
                        typeCache = re.sub('[\[\]]','',types.group(2)) if types.group(2) else ''
                        typeLog = types.group(1).strip()
                        if icons and typeLog and typeLog in typeIcons.keys():
                            post = iconBadgeTemplate%typeIcons[typeLog] + post
                            if 'favorite' in log:
                                favorite = iconFavoriteTemplate
                            log = typeLog
                        if icons and typeCache and typeCache in typeIcons.keys():
                            post = iconPostTemplate%typeIcons[typeCache] + post
                        log = favorite + log
                    post = '<div class="alignleft">' + post + '</div>'
                    if len(elements) > 3:
                        log = '<a href="' + elements[3] + '" target="_blank">' + log + '</a>'
                        currentAdditionalURL = elements[3]
                    log = '<div class="alignright">' + log + '</div>'
                post = '<a href="' + elements[1] + '" target="_blank">' + post + '</a>' + log
            else:
                currentLocation = post
                currentURL = ''
                currentAdditionalURL = ''
            fOut.write(postBegin + post + postMiddle)

        elif tag == '<text>':
            # list of paragraphs
            fOut.write('<div style="clear: both;"></div>')
            text = text +'</p><p>' if text != '' else ''
            text = text + cleanText(l, False)

        elif tag == '<split/>':
            # splitting image table by terminating gallery
            print('Splitting table')

        elif tag == '<page/>':
            # start a new page : to be used to optimize the printing version
            if printing:
                fOut.write('<div class="page-break"  style="page-break-before:always;"></div>\n')

        elif tag in ['<image>', '</image>', '<pano>', '</pano>', '</text>']:
            # already processed
            pass
        else:
            if tag in ['<pre>','<code>']:
                preformatted = True
            elif tag in ['</pre>','</code>']:
                preformatted = False
            text = text + cleanText(l, False)
            if preformatted: text = text + '\n'
        l = f.readline()

    # flush remaining images if any
    flushGallery(fOut, pictures, groupPanoramas, compactGallery)

    fOut.write(postEnd)
    fOut.write(htmlEnd)
    fOut.close()

    print("Result file:", htmlOutput)

    if (mosaic):
        try:
            print("Creating mosaic page",mosaic)
            fOut = open(mosaic,'w')
            fOut.write(headerStart)
            fOut.write(headerMosaic)
            fOut.write(headerPopup)
            fOut.write(bodyMosaic)
            fOut.write('<div class="mosaic">')

            kPictures = allPictures.keys()
            kPictures.sort()
            for k in kPictures:
                for (comment, location, url1, url2, cacheName) in allPictures[k]:
                    fOut.write('<a onclick="popImage(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\');"><img class="thumb" title="%s" src="%s" /></a>\n'%(k,safeString(comment),url1,url2,safeString(cacheName),comment,k))
            fOut.write('</div>\n')
            fOut.write(htmlEnd)
            fOut.close()
        except Exception as msg:
            print("Problem creating mosaic page :",mosaic, msg)


if __name__ == "__main__":
    def usage():
        """
        print(help on program)
        """

        print('Usage: python xml2print.py [-p|--printing] [-g|--groupPanoramas] [-c|--compactGallery] logbook.xml logbook.html')
        sys.exit()

    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hipgcm:", ['help', 'icons', 'printing', 'groupPanoramas','compactGallery','mosaic'])
    except getopt.GetoptError:
        usage()

    printing = False
    groupPanoramas = False
    compactGallery = False
    mosaic = None
    icons = False
    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt == "-p":
            printing = True
        elif opt == "-g":
            groupPanoramas = True
        elif opt == "-c":
            compactGallery = True
        elif opt == "-m":
            mosaic = arg
        elif opt == "-i":
            icons = True

    if len(args) == 2:
        try:
            xml2print(args[0], args[1], printing, groupPanoramas, compactGallery, mosaic, icons)
        except Exception as msg:
            print("Problem:",msg)
        print("That's all, folks!")
    else:
        usage()
