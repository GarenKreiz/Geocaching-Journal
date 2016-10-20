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

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
os.environ['LC_ALL'] = 'fr_FR.UTF-8'

# title and description of the logbook
bookTitle="""Journal de géocaching<br/>Eté 2016"""
bookDescription="""Comptes-rendus des activités géocachiques de Garenkreiz, publiés dans l\'ordre chronologique, incluant les sorties terrain pour la recherche de caches ou la maintenance ainsi que les notes publiées, accompagnés de photos prises à l\'occasion, pour conserver souvenir de bons moments et belles découvertes."""

# jump to a given pattern while analysing a file
def skipTo(fIn, searchString):
    p = re.compile(searchString)
    l = fIn.readline()
    while l <> '' and (not p.search(l)):        
        l = fIn.readline()
    return l

def formatDate(date):
    (year,month,day) = date.split('/')
    strTime = date+" 00:00:01Z"
    t=0
    for pattern in ["%d/%m/%Y %H:%M:%SZ", "%Y/%m/%d %H:%M:%SZ", "%d %b %y %H:%M:%SZ"]:
        try:
          t = int(time.mktime(time.strptime(strTime, pattern)))
        except:
            pass

    date = time.strftime('%A %d %B %Y', time.localtime(t))
    date = date.decode(locale.getpreferredencoding()).encode('utf8')
    date = re.sub(' 0',' ',date)
    return date


class Logbook:

    def __init__(self,fNameInput,fNameOutput="logbook.xml"):
        self.fIn = open(fNameInput,'r')
        self.fXML = open(fNameOutput,"w")
        self.fNameOutput = fNameOutput

    # analyses the HTML content of a log page
    def parseLog(self,data,d,l,c,t,s):
        text = ''
        images = {}
        #print 'Log:',l,c,t,s
        
        self.fXML.write('<post>%s | http://www.geocaching.com/seek/cache_details.aspx?guid=%s |'%(t,c))
        self.fXML.write('%s | http://www.geocaching.com/seek/log.aspx?LUID=%s</post>\n'%(s,l))
                   
        tBegin = data.find('_LogText">')
        if tBegin > 0:
            tBegin += len('_LogText">')
            tEnd = data.find('</span>',tBegin)
            if tEnd > 0:
                text = data[tBegin:tEnd]
        self.fXML.write('<text>%s</text>\n'%text)
        
        listPanoramas=[]
        listImages=[]

        #g = data.find('_GalleryList"',tEnd)
        g = data.find('LogImagePanel',tEnd)
        if g > 0:
            p = g
            p = data.find('<img ',p+1)
            while p > 0:
                # finding the URL of the image
                sBegin = data.find('src="',p)
                sEnd = data.find('"',sBegin+5)
                src = data[sBegin+5:sEnd]
                if not re.search('cache/log',src):
                    print '!!!! Bad image:',src
                    continue
                # normalize form : http://img.geocaching.com/cache/log/display/*.jpg
                
                # src = re.sub('.*(thumb|display)','Images',src)   # to use if there is a local cache of images
                src = re.sub('thumb','display',src)                # to use to access images on geocaching site

                # finding the title of the image
                patternB = re.compile('<(small|span|strong)[^>]*>')
                patternE = re.compile('</(small|span|strong)[^>]*>')
                searchResult = patternB.search(data,sEnd)
                tBegin = searchResult.end()                  # begin of tag
                tEnd = patternE.search(data,tBegin).start()  # end of tag
                title = re.sub('<[^>]*>','',data[tBegin:tEnd])
                if title.find('Click image to view original') <> -1:
                    searchResult = patternB.search(data,tEnd+2)
                    tBegin = searchResult.end()                 # begin of tag
                    tEnd = patternE.search(data,tBegin).start()  # end of tag
                    title = re.sub('<[^>]*>','',data[tBegin:tEnd])
                title = title.strip(' \n\r\t')
                
                # images with "panorama" or "panoramique" in the title are supposed to be wide pictures
                if re.search('panoram', title, re.IGNORECASE):
                    if not (src,title) in listPanoramas:
                        listPanoramas.append((src,title))
                else:
                    if not src in listImages:
                        # at this point, no information is available on the size of image
                        # assume a standard format 640x480 (nostalgia of the 80's?)
                        self.fXML.write("<image>%s<height>480</height><width>640</width><comment>%s</comment></image>\n"%(src,title))
                        listImages.append(src)
                try:
                    images[l].append((src,title))
                except:
                    images[l] = ((src,title))
                    
                # goto next image
                p = data.find('<img alt=',p+1)
                
            # panoramas are displayed after the other images
            # each on a separate line
            if listPanoramas <> []:
                for (src,title) in listPanoramas:
                    self.fXML.write("<pano>%s<height>480</height><width>640</width><comment>%s</comment></pano>\n"%(src,title))

        # identifying logs without image            
        try:
            foo = images[l][0]
        except:
            print "!!!! Log without image:",l,d,t


    # analyse of the HTML page with all the logs of the geocacher
    # local dump of the web page https://www.geocaching.com/my/logs.aspx?s=1
    def processLogs(self):
        self.fXML.write('<title>'+bookTitle+'</title>\n')
        self.fXML.write('<description>'+bookDescription+'</description>\n')

        logs = {}
        days = {}

        l = None
        resu = None
        while resu <> '':
            # to be improved!!!!
            typeLog = skipTo(self.fIn,'/images/logtypes')
            typeLog = re.sub('.*alt="','',typeLog)
            typeLog = re.sub('".*','',typeLog)
            typeLog = re.sub('[\n\r]','',typeLog)
            resu = skipTo(self.fIn,'<td>')
            resu = skipTo(self.fIn,'<td>')
            dateLog = self.fIn.readline()
            dateLog = re.sub('[ \n\r]','',dateLog)
            resu = skipTo(self.fIn,'cache_details')
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
            if idLog <> '':
                logs[idLog] = (dateLog,cacheLog,nameLog,typeLog)
                try:
                    days[dateLog].append((idLog,cacheLog,nameLog,typeLog))
                except:
                    days[dateLog] = [(idLog,cacheLog,nameLog,typeLog)]
            else:
                print "=========================================", resu
            
            print "%s|%s|%s|%s|%s"%(idLog,dateLog,cacheLog,nameLog,typeLog)

        dates = days.keys()
        dates.sort()
        for d in dates:
            self.fXML.write('<date>%s</date>\n'%formatDate(d))
          
            dayLogs = days[d]
            dayLogs.reverse()
            for (l,c,t,s) in dayLogs:
                # building a local cache of the HTML page of each log
                # directory: Logs and 16 sub-directories based on the first letter
                dir = 'Logs/_%s_/'%l[0]
                if not os.path.isfile(dir+l):
                    if not os.path.isdir(dir):
                        print "Creating directory "+dir
                        os.makedirs(dir)
                    url = 'http://www.geocaching.com/seek/log.aspx?LUID='+l
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
                self.parseLog(data,d,l,c,t,s)
        self.fXML.write('<date>Source : GarenKreiz/Geocaching-Journal @ GitHub (CC BY-NC 3.0 FR)</date>\n')
        print 'Logs: ',len(logs), 'Days:',len(dates)
        print 'Result file:', self.fNameOutput 

if __name__=='__main__':
      def usage():
          print 'Usage: python processLogs.py geocaching_logs.html logbook.xml'
          print ''
          print '   where geocaching_log.html is a dump of the web page containing all you logs'
          
      if len(sys.argv) == 3:
          Logbook(sys.argv[1],sys.argv[2]).processLogs()
      else:
          usage()
