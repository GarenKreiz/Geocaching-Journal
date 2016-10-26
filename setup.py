#! python
#
#  Setup for Geocaching-Journal
# 
#  Windows
#      launch with "python setup.py py2exe"
#      wil generate libraries and 2 Windows executables in "dist" directory : processLogs.exe xml2print.exe
#
#  MacOS
#      launch with "python setup.py py2app"
#      not tested
#
#  Versions
#      Python      2.7.11 (AMD64)
#      Py2exe      0.6.9  (AMD64)

from distutils.core import setup
import py2exe

setup(console=['processLogs.py','xml2print.py'])
