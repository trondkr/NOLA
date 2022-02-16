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


o = OceanDrift(loglevel=20) #logfile='log.txt')
start_time='2018-3-1-0'
stop_time='2018-3-16-0'
run_name = 'inner_middle_outer'

#Readers
reader_coast = reader_shape.Reader.from_shpfiles('coast/po10_coast.shp')
o.add_reader(reader_coast) # Add coastline identical to the FVCOM grid

#reader_wind = reader_netcdf_CF_generic('/work/olean/fvcom/run/MATNOC/PO10/Forcing/PO10_wnd_20171201-20180630.nc')
# - not working with generic or unstructured

proj = "+proj=utm +zone=33W, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

fl = Filelist('fileList.txt', start_time=start_time, stop_time=stop_time) # List of path to forcing
unique_files = fl.unique_files()

for f in unique_files:
    print(f)
    fvcom = reader_netCDF_CF_unstructured.Reader(filename=f, proj4=proj)

    o.add_reader(fvcom) 

#Configuration 
o.set_config('general:use_auto_landmask',False) # Override default landmask
o.set_config('general:coastline_action', 'previous') # Jump back to previous position when meeting coast
o.set_config('drift:vertical_mixing',True) # Move particles vertically according to eddy diffusivity and buoyancy 
o.set_config('vertical_mixing:diffusivitymodel', 'windspeed_Sundby1983')
o.set_config('drift:vertical_advection',True) # Move particles vertically according to vertical ocean currents
o.set_config('environment:fallback:sea_surface_wave_stokes_drift_x_velocity',.2)
#o.set_config('drift:current_uncertainty',2) #Not used
#o.set_config('drift:wind_uncertainty',2)

N = 10 # Number of particles
#z = -10 * np.random.uniform(0, 1, N)
z = -5 # Particle depth
#Måselvsutløpet
lon_m_inner = [18.5047601] 
lat_m_inner = [69.2452673]
lon_m_middle = [18.5160648] 
lat_m_middle = [69.2769774] 
lon_m_outer = [18.5326005] 
lat_m_outer = [69.3019249] 
#Aursfjordbotn
#lon_a = [18.7029564]
#lat_a = [69.2612744]
#Nordfjordbotn
#lon_n = [18.9946535]
#lat_n = [69.2933032]

#utm33 = Proj(proj)
#x1, y1 = utm33(lon1, lat1)

#start_times = [datetime(2018, 4, 1, 0), datetime(2018, 4, 2, 0)] # Seed at specific times
start_times = [fl.datetime[0] + timedelta(days=n) for n in range(0, 14, 1)] # Seed at multiple times
for t in start_times:
    o.seed_elements(lon=lon_m_inner, lat=lat_m_inner, z=z, time=t, number=N, radius=20, origin_marker=0) 
    o.seed_elements(lon=lon_m_middle, lat=lat_m_middle, z=z, time=t, number=N, radius=20, origin_marker=1)
    o.seed_elements(lon=lon_m_outer, lat=lat_m_outer, z=z, time=t, number=N, radius=20, origin_marker=2)


# Running model
outfile = '../results/%s_%s_to_%s.nc'%(run_name,start_time,stop_time)
o.run(time_step=3600, end_time=fl.datetime[-1], time_step_output=3600*24, outfile=outfile, export_buffer_length=4)

# Show output
#o.plot(fast=True, linecolor='origin_marker', legend=['Målselv','Aursfjord','Nordfjord'],colorbar=False,filename='drift_plot.png')
#o.plot_property('z')
#o.plot_property('z', mean=True)
#o.animation(fast=True, color='origin_marker', legend=['Målselv','Aursfjord','Nordfjord'],colorbar=False,filename='drift_animation.mp4')
