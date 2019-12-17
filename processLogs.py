#! python
# -*- coding: utf-8 -*-

"""
################################################################################
#
# processLog.py
#
#      process the www.geocaching.com logs for a given geocacher
#      generate a summary in XML format
#
# Copyright GarenKreiz at  geocaching.com or on  YouTube
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
import os
import sys
import time
import codecs
import locale
import urllib2

#os.environ['LC_ALL'] = 'fr_FR.UTF-8'
#locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
locale.setlocale(locale.LC_ALL, '')

# default title and description of the logbook (should be in logbook_header.xml)
bookTitle = u"""<title>Titre à parametrer<br/> Customizable title</title>"""
bookDescription = u"""<description>Description du journal - Logbook description - Fichier à modifier : logbook_header.xml - Modify file : logbook_header.xml</description>"""

class Logbook(object):
    """
    Logbook : generate a list of logs with images for a geocacher
    """
    # directories to save logs (different for TB to avoid conflicts
    dirLog = { 'C': 'Logs', 'L': 'Logs', 'T':'LogsTB'}
    # urls for different types of logs
    urlsLogs = { 'C': 'seek', 'L': 'seek', 'T': 'track'}
    # urls for cacherss, caches and trackable
    urls = { 'C': 'profile', 'L': 'seek/cache_details.aspx', 'T': 'track/details.aspx'}

    def __init__(self,
                 fNameInput, fNameOutput="logbook.xml",
                 verbose=True, startDate=None, endDate=None, refresh=False, excluded=[]):
        self.fNameInput = fNameInput
        self.fNameOutput = fNameOutput
        self.fXML = codecs.open(fNameOutput, "w", 'utf-8')
        self.verbose = verbose
        self.startDate = startDate
        self.endDate = endDate
        self.refresh = refresh
        self.excluded = excluded

        self.nDates = 0          # number of processed dates
        self.nLogs = 0           # number of processed logs


    def getLog(self, dateLog, idLog, idCache, titleCache, typeLog, natureLog):
        
        dirLog = Logbook.dirLog[natureLog] + '/_%s_/'%idLog[0]
        if not os.path.isfile(dirLog+idLog) or self.refresh:
            if not os.path.isdir(dirLog):
                print "Creating directory "+dirLog
                os.makedirs(dirLog)
            url = 'http://www.geocaching.com/'+Logbook.urlsLogs[natureLog]+'/log.aspx?LUID='+idLog
            print "Fetching log", url
            try:
                dataLog = urllib2.urlopen(url).read().decode('utf-8')
                print "Saving log file "+idLog
                with codecs.open(dirLog+idLog, 'w', 'utf-8') as fw:
                    fw.write(dataLog)
            except (urllib2.HTTPError, urllib2.URLError), msg:
                print "Error accessing log "+idLog, msg
                return
        else:
            with codecs.open(dirLog+idLog, 'r', 'utf-8') as fr:
                if self.verbose:
					try:
						print "Processing cache " + titleCache
					except:
						print "Processing cache %r"%titleCache
                dataLog = fr.read()
        return self.parseLog(dataLog, dateLog, idLog, idCache, titleCache, typeLog, natureLog)


    def parseLog(self, dataLog, dateLog, idLog, idCache, titleCache, typeLog, natureLog):
        """
        analyses the HTML content of a log page
        """

        text = ''
        listeImages = []

        if natureLog == 'T' and 'cache_details.aspx' in dataLog:
            # adding the name of the cache where the trackable is, if present in the log
            titleTb = re.search('cache_details.aspx\?guid=([^>]*)">(.*?)</a>', dataLog, re.S).group(2)
            titleCache = titleCache + ' @ ' + titleTb

        if '_LogText">' in dataLog:
            text = re.search('_LogText">(.*?)</span>', dataLog, re.S).group(1)
            text = re.sub('src="/images/', 'src="http://www.geocaching.com/images/', text)
        else:
            print "!!!! Log unavailable", idLog

        if 'LogBookPanel1_GalleryList' in dataLog: #if Additional images
            tagTable = re.search('<table id="ctl00_ContentBody_LogBookPanel1_GalleryList(.*?)</table>',dataLog, re.S).group(0)
            title = re.findall('<img alt=\'(.*?)\' src', tagTable, re.S)
            title = [re.sub(' log image', "", result) for result in title]
            url = re.findall('src="(.*?)" />', tagTable, re.S)
            url = [re.sub('log/.*/', "log/display/", result) for result in url] # normalize form : http://img.geocaching.com/cache/log/display/*.jpg
            for index, tag in enumerate(url):
                panora = self.__isPanorama(title[index])
                listeImages.append((url[index], title[index], panora))
        elif 'LogBookPanel1_ImageMain' in dataLog: #if single images
            urlTitle = re.search('id="ctl00_ContentBody_LogBookPanel1_ImageMain(.*?)href="(.*?)" target(.*?)span class="logimg-caption">(.*?)</span><span>',dataLog, re.S)
            panora = self.__isPanorama(urlTitle.group(4))
            listeImages.append((urlTitle.group(2), urlTitle.group(4), panora))
        else:
            print u'!!!! Log without image', idLog, dateLog, u'%r'%titleCache,'>>>',typeLog

        return (titleCache,text,listeImages)

    def outputLog(self, dateLog, idLog, idCache, titleCache, typeLog, natureLog, textLog, listeImages):
        """
        analyses the HTML content of a log page
        """

        self.fXML.write('<post>%s | http://www.geocaching.com/%s?guid=%s |'%(titleCache, Logbook.urls[natureLog], idCache))
        self.fXML.write('%s | http://www.geocaching.com/%s/log.aspx?LUID=%s</post>\n'%(typeLog, Logbook.urlsLogs[natureLog], idLog))

        self.fXML.write('<text>%s</text>\n'%textLog)

        # listeImages.sort(key=lambda e: e[2]) # panoramas are displayed after the other images - sort by field panora

        for (img, caption, panora) in listeImages:
            typeImage = ('pano' if panora else 'image')
            # at this point, no information is available on the size of image
            # assume a standard format 640x480 (nostalgia of the 80's?)
            if typeImage == 'pano':
                img = re.sub('/display/', '/', img)
            self.fXML.write("<%s>%s<height>480</height><width>640</width><comment>%s</comment></%s>\n"%(typeImage, img, caption, typeImage))
    
    # images with "panorama" or "panoramique" in the caption are supposed to be wide pictures
    def __isPanorama(self, title):
        return (True if re.search('panoram', title, re.IGNORECASE) else False)

    def processLogs(self):
        """
        analyse of the HTML page with all the logs of the geocacher
        local dump of the web page https://www.geocaching.com/my/logs.aspx?s=1
        """

        try:
            with codecs.open('logbook_header.xml', 'r', 'utf-8') as f:
                self.fXML.write(f.read())
        except:
            self.fXML.write('<title>' + bookTitle + '</title>\n')
            self.fXML.write('<description>' + bookDescription + '</description>\n')

        allLogs = 0
        days = {}

        idLog = None
        with codecs.open(self.fNameInput, 'r', 'utf-8') as fIn:
            cacheData = fIn.read()

        # natureLog : C for caches, L for logs, T for trackables
        natureLog = re.search('<body([^>]*)', cacheData).group(1)
        natureLog = 'C' if re.search('CacheDetail',natureLog) else 'L' # T detected later
        if natureLog == 'C':
            tagTable = re.search('<table id="cache_logs_table"[^>]*>(.*)</table>', cacheData, re.S|re.M).group(1)
        else:
            tagTable = re.search('<table class="Table">(.*)</table>', cacheData, re.S|re.M).group(1)
        tagTr = re.finditer('<tr(.*?)</tr>', tagTable, re.S)
        listTr = [result.group(1) for result in tagTr]
        for tr in listTr:
            td = re.finditer('<td>(.*?)</td>', tr, re.S)
            listTd = [result.group(1) for result in td]
            imagesList = []
            if natureLog == 'C':
                # TODO : detect images
                if  len(listTd) == 0:
                    break
                divs = re.search('href="([^"]*")[^>]*>([^<]+)</a>.*title="(.+)" alt.*LogDate">(.+)</span>.*LogText">(.*)</div>.*href="([^"]+")',listTd[0], re.S)
                textLog = divs.group(5)
                dateLog = self.__normalizeDate(divs.group(4))
                typeLog = divs.group(3)
                typeCache = ''
                idCache = re.search('guid=(.*?)"', divs.group(1)).group(1)
                idLog = re.search('LUID=(.*?)"',divs.group(6)).group(1)
                titleCache =  divs.group(2)
            else:
                textLog = None
                dateLog = self.__normalizeDate(listTd[2].strip())
                typeLog = re.search('title="(.*)".*>', listTd[0]).group(1)
                if re.search('Favorited',listTd[1]):
                    typeLog = typeLog + ' [favorite]'
                idCache = re.search('guid=(.*?)"', listTd[3]).group(1)
                typeCache = re.search('title="([^"]*)"', listTd[3]).group(1)
                idLog = re.search('LUID=(.*?)"', listTd[5]).group(1)
                titleCache = re.search('</a> <a(.*)?\">(.*)</a>', listTd[3]).group(2).replace('</span>', '')
                natureLog = ('L' if listTd[3].find('cache_details') > 1 else 'T') # C for Cache and T for trackable
            allLogs += 1
            if (typeCache):
                typeLog += ' [%s]'%typeCache
            # keeping the logs that are not excluded by -x option
            #keep = (True if typeLog.lower() in [item.lower() for item in self.excluded] else False)
            #test short string research exclude - ex : -x Write for Write note or -x Found for Found it - etc.
            keepLog = (False if len([excluded for excluded in self.excluded if excluded.lower() in typeLog.lower()]) else True)
            if keepLog and idLog <> '':
                try:
                    days[dateLog].append((idLog, idCache, titleCache, typeLog, natureLog, textLog, imagesList))
                except KeyError:
                    days[dateLog] = [(idLog, idCache, titleCache, typeLog, natureLog, textLog, imagesList)]
                if self.verbose:
					try:
						print "%s|%s|%s|%s|%s|%s"%(idLog, dateLog, idCache, titleCache, typeLog, natureLog)
					except:
						print "%s|%s|%s|%r|%s|%s"%(idLog, dateLog, idCache, titleCache, typeLog, natureLog)
        dates = days.keys()
        dates.sort()
        for dateLog in dates:
            # check if date is in the correct interval
            if self.startDate and dateLog < self.startDate:
                continue
            if self.endDate and dateLog > self.endDate:
                continue
            self.nDates += 1
            self.fXML.write('<date>%s</date>\n'%self.__formatDate(dateLog))

            dayLogs = days[dateLog]
            dayLogs.reverse()
            for (idLog, idCache, titleCache, typeLog, natureLog, textLog, imagesList) in dayLogs:
                self.nLogs += 1
                # logId, cacheId or tbID, title, type, nature
                # building a local cache of the HTML page of each log
                # directory: Logs and 16 sub-directories based on the first letter

                if not textLog:
                    (cacheTitle, textLog, imagesList) = self.getLog(dateLog, idLog, idCache, titleCache, typeLog, natureLog)
                self.outputLog(dateLog, idLog, idCache, titleCache, typeLog, natureLog, textLog, imagesList)

        self.fXML.write('<date>Source : GarenKreiz/Geocaching-Journal @ GitHub (CC BY-NC 3.0 FR)</date>\n')
        self.fXML.close()
        print 'Logs: ', self.nLogs, '/', allLogs, 'Days:', self.nDates, '/', len(dates)
        print 'Result file:', self.fNameOutput

    def processCache(self):
        """
        analyse of the HTML page with the cache description and  the logs of the geocachers
        source dump of a geocache page
        """

        try:
            with codecs.open('logbook_header.xml', 'r', 'utf-8') as f:
                self.fXML.write(f.read())
        except:

            self.fXML.write('<title>' + bookTitle + '</title>\n')
            self.fXML.write('<description>' + bookDescription + '</description>\n')

        allLogs = 0
        days = {}

        idLog = None
        with codecs.open(self.fNameInput, 'r', 'utf-8') as fIn:
            cacheData = fIn.read()
        tagTable = re.search('<table id="cache_logs_table"[^>]*>(.*)</table>', cacheData, re.S|re.M).group(1)
        tagTr = re.finditer('<tr(.*?)</tr>', tagTable, re.S)
        listTr = [result.group(1) for result in tagTr]
        for tr in listTr:
            #td = re.finditer('<td>(.*?)</td>', tr, re.S)
            #listTd = [result.group(1) for result in td]
            try:
              td = re.search('<td>(.*?)</td>', tr, re.S).group(1)
            except:
              break
            divs = re.search('href="([^"]*")[^>]*>([^<]+)</a>.*title="(.+)" alt.*LogDate">(.+)</span>.*LogText">(.*)</div>.*href="([^"]+")',td, re.S)
            #listTd = [result.group(1) for result in td]
            profile = divs.group(1)
            user = divs.group(2)
            type = divs.group(3)
            date = divs.group(4)
            textLog = divs.group(5)
            logURL = divs.group(6)
            #dateLog = self.__normalizeDate(listTd[2].strip())
            dateLog = self.__normalizeDate(date)
            #typeLog = re.search('title="(.*)".*>', listTd[0]).group(1)
            typeLog = type
            #idCache = re.search('guid=(.*?)"', listTd[3]).group(1)
            idCache = re.search('guid=(.*?)"', profile).group(1)
            #idLog = re.search('LUID=(.*?)"', listTd[5]).group(1)
            idLog = re.search('LUID=(.*?)"', logURL).group(1)
            #titleCache = re.search('</a> <a(.*)?\">(.*)</a>', listTd[3]).group(2).replace('</span>', '')
            titleCache = user
            #natureLog = ('C' if listTd[3].find('cache_details') > 1 else 'T') # C for Cache and T for trackable
            natureLog = 'L'
            allLogs += 1
 
            # keeping the logs that are not excluded by -x option
            #keep = (True if typeLog.lower() in [item.lower() for item in self.excluded] else False)
            #test short string research exclude - ex : -x Write for Write note or -x Found for Found it - etc.
            keepLog = (False if len([excluded for excluded in self.excluded if excluded.lower() in typeLog.lower()]) else True)
            if keepLog and idLog <> '':
                try:
                    days[dateLog].append((idLog, idCache, titleCache, typeLog, natureLog, textLog))
                except KeyError:
                    days[dateLog] = [(idLog, idCache, titleCache, typeLog, natureLog, textLog)]
                if self.verbose:
                    print "%s|%s|%s|%s|%s|%s"%(idLog, dateLog, idCache, titleCache, typeLog, natureLog)
        dates = days.keys()
        dates.sort()
        for dateLog in dates:
            # check if date is in the correct interval
            if self.startDate and dateLog < self.startDate:
                continue
            if self.endDate and dateLog > self.endDate:
                continue
            self.nDates += 1
            self.fXML.write('<date>%s</date>\n'%self.__formatDate(dateLog))

            dayLogs = days[dateLog]
            dayLogs.reverse()
            for (idLog, idCache, titleCache, typeLog, natureLog, textLog) in dayLogs:
                self.nLogs += 1
                # logId, cacheId or tbID, title, type, nature
                # building a local cache of the HTML page of each log
                # directory: Logs and 16 sub-directories based on the first letter

                # grabbing information from the log page
                if textLog == '':
                    self.parseLog(dataLog, dateLog, idLog, idCache, titleCache, typeLog, natureLog)
                else:
                    self.outputLog(dateLog, idLog, idCache, titleCache, typeLog, natureLog, textLog, [])

        self.fXML.write('<date>Source : GarenKreiz/Geocaching-Journal @ GitHub (CC BY-NC 3.0 FR)</date>\n')
        self.fXML.close()
        print 'Logs: ', self.nLogs, '/', allLogs, 'Days:', self.nDates, '/', len(dates)
        print 'Result file:', self.fNameOutput

    def __formatDate(self, date):
        """
        format date in readable form, according to local settings
        """

        strTime = date+" 00:00:01Z"
        t = 0
        try:
            t = int(time.mktime(time.strptime(strTime, "%Y/%m/%d %H:%M:%SZ")))
        except:
            pass
        date = time.strftime('%A %d %B %Y', time.localtime(t))
        date = date.decode(locale.getpreferredencoding()).encode('utf8')
        date = re.sub(' 0', ' ', date)
        return date.decode('utf-8')

    def __normalizeDate(self, date):
        """
        mormalize date in YYYY/MM/DD form
        """

        date = re.sub('[-. ]+', '/', date)
        date = re.sub('/+$', '', date)
        (y, m, d) = date.split('/')
        if int(m) > 12:
            print "Date format month/day/year not supported. Choose another format in the web site preferences (day/month/year)."
        if int(d) > 1969:
            # dd.mm.yyyy
            d, y = y, d
        elif int(y) < 1970:
            # dd.mm.yy
            d, y = y, int(d)+2000
        date = '%02d/%02d/%02d'%(int(y), int(m), int(d))
        return date

if __name__ == '__main__':
    def usage():
        print 'Usage: python processLogs.py [-q|--quiet] geocaching_logs.html logbook.xml'
        print '    or python processLogs.py [-q|--quiet] geocaching_logs.html logbook.html'
        print ''
        print '   geocaching_logs.html'
        print '       dump of the web page containing all you logs (HTML only)'
        print '       sauvegarde de la page contenant tous vos logs (HTML uniquement)'
        print '   logbook.xml'
        print '       content of all log entries with reference to pictures'
        print '       contenu de tous les logs avec references aux images'
        print '   logbook.html'
        print '       web page with all logs and images (using xml2print.py)'
        print '       page web avec tous les logs et images (utilise xml2print.py)'
        print ''
        print '   -q|--quiet'
        print '       less verbose console output'
        print '       execution du programme moins verbeuse'
        print '   -s|--start startDate'
        print '       start processing log at date startDate (included, format YYYY/MM/DD)'
        print '       commence le traitement des logs a partir de la date startDate incluse (format AAAA/MM/JJ)'
        print '   -e|--end endDate'
        print '       stop processing log after date endDate (format YYYY/MM/DD)'
        print '       arrete le traitement des logs apres la date endDate (format AAAA/MM/JJ)'
        print '   -r|--refresh'
        print '       refresh local cache of logs (to use when the log was changed or pictures were added)'
        print '       rafraichit la version locale des journaux (a utiiser si des modifications ont ete faites ou des photos ont ete ajoutees'
        print '   -x|--exclude'
        print '       exclude a given log type, can be repeated (for example "-x update -x disable")'
        print '       exclusion de certains types de log, par recherche de chaine de caractere (par exemple "-x update -x disable")'

        sys.exit()

    import getopt

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hcrqs:e:x:", ['help', 'cache', 'refresh', 'quiet', 'start', 'end', 'exclude'])
    except getopt.GetoptError:
        usage()

    verbose = True
    startDate = None
    endDate = None
    refresh = False
    excluded = []

    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt == "-q":
            verbose = False
        elif opt == "-r":
            refresh = True
        elif opt == "-s":
            if len(arg.split('/')) <> 3:
                print "!!! Bad start date format, use YYYY/MM/DD"
                print "!!! Format de date de debut faux, utiliser AAAA/MM/JJ"
                sys.exit(1)
            startDate = arg
        elif opt == "-e":
            if len(arg.split('/')) <> 3:
                print "Bad end date format, use YYYY/MM/DD"
                print "Format de date de fin faux, utiliser AAAA/MM/JJ"
                sys.exit(1)
            endDate = arg
        elif opt == "-x":
            excluded.append(arg)

    print "Excluded:", excluded

    if len(args) == 2:
        if re.search(".xml", args[0], re.IGNORECASE):
            xmlFile = args[0]
        elif re.search(".xml", args[1], re.IGNORECASE):
            xmlFile = args[1]
        else:
            xmlFile = "logbook.xml"

        # firt phase : from Groundspeak HTML to XML
        if re.search(".htm[l]*", args[0], re.IGNORECASE):
            Logbook(args[0], xmlFile, verbose, startDate, endDate, refresh, excluded).processLogs()

        # second phase : from XML to generated HTML
        if re.search(".htm[l]*", args[1], re.IGNORECASE):
            import xml2print
            xml2print.xml2print(xmlFile, args[1], printing=False, groupPanoramas=True, compactGallery=True)
        print "That's all folks!"
    else:
        usage()
