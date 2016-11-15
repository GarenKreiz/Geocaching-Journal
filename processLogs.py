#! python
# -*- coding: utf-8 -*-
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

import re
import os
import sys
import time
import random
import locale
import urllib2
import datetime

#os.environ['LC_ALL'] = 'fr_FR.UTF-8'
#locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
locale.setlocale(locale.LC_ALL, '')

# default title and description of the logbook (should be in logbook_header.xml)
bookTitle="""<title>Titre à paramétrer<br/> Customizable title</title>"""
bookDescription="""<description>Description du journal - Logbook description - Fichier à modifier : logbook_header.xml - Modify file : logbook_header.xml</description>"""


# jump to a given pattern while analysing a file
def skipTo(fIn, searchString):
    p = re.compile(searchString)
    l = fIn.readline()
    while l <> '' and (not p.search(l)):        
        l = fIn.readline()
    return l

def normalizeDate(date):
    date = date[6:10] + '/' + date[0:2]  + '/' + date[3:5]
    return date
    

def formatDate(date):
    (year,month,day) = date.split('/')
    strTime = date+" 00:00:01Z"
    t=0
    try:
        t = int(time.mktime(time.strptime(strTime, "%Y/%m/%d %H:%M:%SZ")))
    except:
        pass
    
    date = time.strftime('%A %d %B %Y', time.localtime(t))
    date = date.decode(locale.getpreferredencoding()).encode('utf8')
    date = re.sub(' 0',' ',date)
    return date


class Logbook:

    def __init__(self,
                 fNameInput, fNameOutput="logbook.xml",
                 verbose=True, localImages=False, startDate = None, endDate = None, refresh = False, excluded = []):
        self.fIn = open(fNameInput,'r')
        self.fXML = open(fNameOutput,"w")
        self.fNameOutput = fNameOutput
        self.verbose = verbose
        self.localImages = localImages
        self.startDate = startDate
        self.endDate = endDate
        self.refresh = refresh
        self.excluded = excluded
        
        self.nDates = 0          # number of processed dates
        self.nLogs = 0           # number of processed logs

    # analyses the HTML content of a log page
    def parseLog(self,data,day,logID,cacheID,title,status,nature):
        text = ''
        images = {}
        #print 'Log:',logID,cacheID,title,status

        if nature == 'C':
            url = 'seek/cache_'
            urlLog='seek'
        else:
            url = 'track/'
            urlLog = 'track'
        self.fXML.write('<post>%s | http://www.geocaching.com/%sdetails.aspx?guid=%s |'%(title,url,cacheID))
        self.fXML.write('%s | http://www.geocaching.com/%s/log.aspx?LUID=%s</post>\n'%(status,urlLog,logID))
                   
        tBegin = data.find('_LogText">')
        if tBegin > 0:
            tBegin += len('_LogText">')
            tEnd = data.find('</span>',tBegin)
            if tEnd > 0:
                text = data[tBegin:tEnd]
        else:
            self.fXML.write('<text> </text>\n')
            print "!!!! Log unavailable",logID
            return
        if self.localImages:
            text = re.sub('src="/images/','src="Images/',text)                
        else:
            text = re.sub('src="/images/','src="http://www.geocaching.com/images/',text)    
        self.fXML.write('<text>%s</text>\n'%text)
        
        listPanoramas=[]
        listImages=[]

        #g = data.find('_GalleryList"',tEnd)
        g = data.find('LogImagePanel',tEnd)
        if g > 0:
            p = data.find('<img ',g+1)
            while p > 0:
                # finding the URL of the image
                sBegin = data.find('src="',p)
                sEnd = data.find('"',sBegin+5)
                src = data[sBegin+5:sEnd]
                if not re.search('(cache|track)/log/',src):
                    print '!!!! Bad image:',src
                    p = data.find('<img ',p+4)
                    continue
                
                # normalize form : http://img.geocaching.com/cache/log/display/*.jpg
                if self.localImages:
                    src = re.sub('.*(thumb|display)','Images',src)     # to use if there is a local cache of images
                else:
                    src = re.sub('thumb','display',src)                # to use to access images on geocaching site

                # finding the caption of the image
                patternB = re.compile('<(small|span|strong)[^>]*>')
                patternE = re.compile('</(small|span|strong)[^>]*>')
                searchResult = patternB.search(data,sEnd)
                tBegin = searchResult.end()                  # begin of tag
                tEnd = patternE.search(data,tBegin).start()  # end of tag
                caption = re.sub('<[^>]*>','',data[tBegin:tEnd])
                if caption.find('Click image to view original') <> -1:
                    searchResult = patternB.search(data,tEnd+2)
                    tBegin = searchResult.end()                 # begin of tag
                    tEnd = patternE.search(data,tBegin).start()  # end of tag
                    caption = re.sub('<[^>]*>','',data[tBegin:tEnd])
                caption = caption.strip(' \n\r\t')
                
                # images with "panorama" or "panoramique" in the captin are supposed to be wide pictures
                if re.search('panoram', caption, re.IGNORECASE):
                    src = re.sub('/log/display/','/log/',src)     # use full size image for panorama
                    
                    if not (src,caption) in listPanoramas:
                        listPanoramas.append((src,caption))
                else:
                    if not src in listImages:
                        # at this point, no information is available on the size of image
                        # assume a standard format 640x480 (nostalgia of the 80's?)
                        self.fXML.write("<image>%s<height>480</height><width>640</width><comment>%s</comment></image>\n"%(src,caption))
                        listImages.append(src)
                try:
                    images[logID].append((src,caption))
                except:
                    images[logID] = ((src,caption))
                    
                # goto next image
                p = data.find('<img alt=',p+1)
                
            # panoramas are displayed after the other images
            # each on a separate line
            if listPanoramas <> []:
                for (src,caption) in listPanoramas:
                    self.fXML.write("<pano>%s<height>480</height><width>640</width><comment>%s</comment></pano>\n"%(src, caption))

        self.nLogs += 1
        
        # identifying logs without image            
        try:
            foo = images[logID][0]
        except:
            print "!!!! Log without image:",logID,day,title,'>>>',status


    # analyse of the HTML page with all the logs of the geocacher
    # local dump of the web page https://www.geocaching.com/my/logs.aspx?s=1
    def processLogs(self):
        try:
            with open('logbook_header.xml', 'r') as f:
                self.fXML.write(f.read())
        except:
            self.fXML.write('<title>'+bookTitle+'</title>\n')
            self.fXML.write('<description>'+bookDescription+'</description>\n')

        logs = {}
        days = {}

        l = None
        resu = None
        while resu <> '':
            # to be improved!!!!
            typeLog = skipTo(self.fIn,'/images/logtypes')
            if typeLog == '':
                # end of file
                break
            typeLog = re.sub('.*alt="','',typeLog)
            typeLog = re.sub('".*','',typeLog)
            typeLog = re.sub('[\n\r]*','',typeLog)

            resu = skipTo(self.fIn,'<td>')
            resu = skipTo(self.fIn,'<td>')
            # parse date (numerical format only) and transform in canonical form yyyy/mm/dd
            dateLog = self.fIn.readline().strip()
            dateLog = normalizeDate(dateLog)
            
            resu = skipTo(self.fIn,'details')
            if (resu.find('cache_details') > 1):
                logNature = 'C'    # log for a cache
            else:
                logNature = 'T'    # log for a trackable
            resu = re.sub('.*guid=','',resu)
            resu = re.sub('[\n\r]','',resu)
            cacheLog = re.sub('".*','',resu)
            nameLog = re.sub('</a>.*','',resu)
            nameLog = re.sub('</span>','',nameLog)
            nameLog = re.sub('.*>','',nameLog)
            resu = skipTo(self.fIn,'log.aspx')
            idLog = re.sub('.*LUID=','',resu)
            idLog = re.sub('".*','',idLog)
            idLog = re.sub('[ \n\r]','',idLog)

            # keeping the logs that are not excluded by -x option
            keep = True
            for typeExclude in self.excluded:
                keep = keep & (re.search(typeExclude,typeLog,re.IGNORECASE) < 0)
            if keep and idLog <> '':
                logs[idLog] = (dateLog,cacheLog,nameLog,typeLog,logNature)
                try:
                    days[dateLog].append((idLog,cacheLog,nameLog,typeLog,logNature))
                except:
                    days[dateLog] = [(idLog,cacheLog,nameLog,typeLog,logNature)]
                if self.verbose:
                    print "%s|%s|%s|%s|%s|%s"%(idLog,dateLog,cacheLog,nameLog,typeLog,logNature)
            
        dates = days.keys()
        dates.sort()

        for d in dates:
            # check if date is in the correct interval
            if self.startDate and d < self.startDate:
                continue
            if self.endDate and d > self.endDate:
                continue
            self.nDates += 1
            self.fXML.write('<date>%s</date>\n'%formatDate(d))
          
            dayLogs = days[d]
            dayLogs.reverse()
            for (l,c,t,s,logNature) in dayLogs:
                # logId, cacheId or tbID, title, type, nature 
                # building a local cache of the HTML page of each log
                # directory: Logs and 16 sub-directories based on the first letter
                if logNature == 'C':
                    url = 'seek'
                    dir = 'Logs'
                else:
                    url = 'track'
                    dir = 'LogsTB'   # dedicated directory for TB logs as ID may be reused between TB and cache logs 
                dir = dir + '/_%s_/'%l[0]
                if not os.path.isfile(dir+l) or self.refresh:
                    if not os.path.isdir(dir):
                        print "Creating directory "+dir
                        os.makedirs(dir)
                    url = 'http://www.geocaching.com/'+url+'/log.aspx?LUID='+l
                    print "Fetching log",url
                    data = urllib2.urlopen(url).read()
                    print "Saving log file "+l
                    f = open(dir+l,'w')
                    f.write(data)
                    f.close()
                else:
                    f = open(dir+l,'r')
                    data = f.read()
                    f.close()
                # grabbing information from the log page
                self.parseLog(data,d,l,c,t,s,logNature)
                
        self.fXML.write('<date>Source : GarenKreiz/Geocaching-Journal @ GitHub (CC BY-NC 3.0 FR)</date>\n')
        print 'Logs: ',self.nLogs,'/',len(logs), 'Days:',self.nDates,'/',len(dates)
        print 'Result file:', self.fNameOutput 

if __name__=='__main__':
    def usage():
          print 'Usage: python processLogs.py [-q|--quiet] [-l|--local-images] geocaching_logs.html logbook.xml'
          print '    or python processLogs.py [-q|--quiet] [-l|--local-images] geocaching_logs.html logbook.html'
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
          print '   -l|--local-images'
          print '       use local images in directory Images (previously downloaded for example using "wget")'
          print '       utilisation d\'une copie locale des images dans le repertoire Images (telechargees par exemple avec "wget")'
          print '   -s|--start startDate'
          print '       start processing log at date startDate (included, format YYYY/MM/DD)'
          print '       commence le traitement des logs à partir de la date startDate incluse (format AAAA/MM/JJ)'
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
        opts, args = getopt.getopt(sys.argv[1:],"hrqls:e:x:", ['help','refresh','quiet','local-images','start','end','exclude'])
    except getopt.GetoptError:
        usage()

    verbose = True
    localImages = False
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
        elif opt == "-l":
            localImages = True
        elif opt == "-s":
            if len(arg.split('/')) <> 3:
                print "!!! Bad start date format, use YYYY/MM/DD"
                print "!!! Format de date de début faux, utiliser AAAA/MM/JJ"
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

    print "Excluded:",excluded
    
    if len(args) == 2:
        if re.search(".xml", args[0], re.IGNORECASE):
            xmlFile = args[0]
        elif re.search(".xml", args[1], re.IGNORECASE):
            xmlFile = args[1]
        else:
            xmlFile = "logbook.xml"

        # firt phase : from Groundspeak HTML to XML
        if re.search(".htm[l]*", args[0], re.IGNORECASE):
            Logbook(args[0],xmlFile,verbose,localImages,startDate,endDate,refresh,excluded).processLogs()

        # second phase : from XML to generated HTML
        if re.search(".htm[l]*",args[1], re.IGNORECASE):
            import xml2print
            xml2print.xml2print(xmlFile,args[1])

        print "That's all folks!"
    else:
        usage()
        
          
