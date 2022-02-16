#!/usr/bin/env python
"""
FVCOM: Using model input from unstructured grid
===============================================
"""
import sys 
sys.path.append('/work/kvile/opendrift')
import os
from datetime import datetime, timedelta 
from opendrift.readers import reader_netCDF_CF_unstructured # FVCOM reader
from opendrift.models.oceandrift import OceanDrift

from glob import glob
folders = glob("/data/MATNOC/PO10/*/", recursive = True)
folders.sort()
firstfolder = folders[1]
firstfiles = glob(firstfolder+'*')
firstfiles.sort()
firstfile = firstfiles[0]
lastfolder = folders[-1]
lastfiles = glob(lastfolder+'*')
lastfiles.sort()
lastfile = lastfiles[-1]

o = OceanDrift(loglevel=20) 

#Readers
proj = "+proj=utm +zone=33W, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

fvcom_first = reader_netCDF_CF_unstructured.Reader(filename=firstfile, proj4=proj)
print(fvcom_first)

fvcom_last = reader_netCDF_CF_unstructured.Reader(filename=lastfile, proj4=proj)
print(fvcom_last)
