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
from opendrift.readers import reader_netCDF_CF_generic 
from opendrift.readers import reader_netCDF_CF_unstructured # FVCOM reader
from opendrift.readers import reader_shape
from opendrift.models.oceandrift import OceanDrift

o = OceanDrift(loglevel=20,logfile='log.txt')

#Readers
reader_coast = reader_shape.Reader.from_shpfiles('coast/po10_coast.shp')
o.add_reader(reader_coast) # Add coastline identical to the FVCOM grid

#reader_wind = reader_netcdf_CF_generic('/work/olean/fvcom/run/MATNOC/PO10/Forcing/PO10_wnd_20171201-20180630.nc')
# - not working with generic or unstructured

proj = "+proj=utm +zone=33W, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

fl = Filelist('fileList.txt', start_time='2018-3-1-0', stop_time='2018-3-3-0') # List of path to forcing
unique_files = fl.unique_files()

for f in unique_files:
    print(f)
    fvcom = reader_netCDF_CF_unstructured.Reader(filename=f, proj4=proj)

    o.add_reader(fvcom) 

#Configuration 
o.set_config('general:use_auto_landmask',False) # Override default landmask

o.set_config('general:coastline_action', 'previous') # Jump back to previous position when meeting coast


N = 2 # Number of particles
#z = -10 * np.random.uniform(0, 1, N)
z = -5 # Particle depth
#Måselvsutløpet
lon1 = 18.521
lat2 = [69.308, 69.261, 69.289]
#Aursfjordbotn
lon1 = [18.521, 18.696, 18.998]
lat2 = [69.308, 69.261, 69.289]
#Nordfjordbotn
lon1 = [18.521, 18.696, 18.998]
lat2 = [69.308, 69.261, 69.289]


#utm33 = Proj(proj)
#x1, y1 = utm33(lon1, lat1)

start_times = [datetime(2018, 3, 1, 0), datetime(2018, 3, 2, 0)] # Seed at specific times
#start_times = [fl.datetime[0] + timedelta(hours=n) for n in range(0, 24*4, 6)] # Seed at multiple times
for t in start_times:
    o.seed_elements(lon=18.507, lat=69.245, z=z, time=t, number=N, radius=20, origin_marker=0) #Målselv
    o.seed_elements(lon=18.696, lat=69.261, z=z, time=t, number=N, radius=20, origin_marker=1) #Aursfjord 
    o.seed_elements(lon=18.998, lat=69.289, z=z, time=t, number=N, radius=20, origin_marker=2) #Nordfjordbotn


# Running model
o.run(time_step=3600, duration=timedelta(days=3), time_step_output=3600*12, outfile='/work/kvile/results/nola-sis/test1.nc', export_variables=['time', 'lon', 'lat', 'z'], export_buffer_length=4)

# Show output
o.plot(fast=True, linecolor='origin_marker', legend=['Målselv','Aursfjord','Nordfjord'],colorbar=True)
#o.plot_property('z')
#o.plot_property('z', mean=True)
#o.animation
