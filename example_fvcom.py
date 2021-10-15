#!/usr/bin/env python
"""
FVCOM: Using model input from unstructured grid
===============================================
"""
import sys 
sys.path.append('/work/kvile/opendrift')
import os
from datetime import datetime, timedelta
import numpy as np
import cartopy.io.shapereader as shpreader
from pyproj import Proj

from tools import Filelist
from opendrift.readers import reader_netCDF_CF_unstructured # FVCOM reader
from opendrift.readers import reader_shape
from opendrift.models.oceandrift import OceanDrift

#TEST

reader_coast = reader_shape.Reader.from_shpfiles('coast/po10_coast.shp')
o = OceanDrift(loglevel=20)

proj = "+proj=utm +zone=33W, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

fl = Filelist('fileList.txt', start_time='2018-2-1-0', stop_time='2018-2-6-0') # List of path to forcing
unique_files = fl.unique_files()

o.add_reader(reader_coast) # Add coastline identical to the FVCOM grid

# Configuration 
o.set_config('general:use_auto_landmask',False) # Override default landmask

o.set_config('general:coastline_action', 'previous') # Jump back to previous position when meeting coast

for f in unique_files:
    print(f)
    fvcom = reader_netCDF_CF_unstructured.Reader(filename=f, proj4=proj)

    o.add_reader(fvcom)

N = 2 # Number of particles
#z = -10 * np.random.uniform(0, 1, N)
z = -5 # Particle depth
lon1 = 18.697
lat1 = 69.554
#utm33 = Proj(proj)
#x1, y1 = utm33(lon1, lat1)

start_times = [datetime(2018, 2, 2, 0), datetime(2018, 2, 4, 0)] # Seed at specific times
#start_times = [fl.datetime[0] + timedelta(hours=n) for n in range(0, 24*4, 1)] # Seed at multiple times
for t in start_times:
    o.seed_elements(lon=lon1, lat=lat1, radius=10, number=N, z=z, time=t) 


# Running model
o.run(time_step=600, duration=timedelta(days=2), time_step_output=3600, outfile='/work/kvile/results/nola-sis/test1.nc', export_variables=['time', 'lon', 'lat', 'z'], export_buffer_length=4)
