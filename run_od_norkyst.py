#!/usr/bin/env python

import sys 
sys.path.append('/cluster/home/kristokv/opendrift')
sys.path.append('../opendrift')
import os
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
#import cartopy.io.shapereader as shpreader
#from pyproj import Proj

from opendrift.readers import reader_ROMS_native
#from opendrift.readers import reader_netCDF_CF_generic 
#from opendrift.readers import reader_shape
from opendrift.models.oceandrift import OceanDrift

o = OceanDrift(loglevel=20) #logfile='log.txt')

startDay='2018-3-1-1'
endDay='2018-3-7-0'
startTime = datetime.strptime(startDay, '%Y-%m-%d-%H')
endTime = datetime.strptime(endDay, '%Y-%m-%d-%H')
run_name = 'testing_fram'
outfile = '/cluster/projects/nn9297k/NOLA-SIS/results/%s_%s_to_%s.nc'%(run_name,startDay,endDay)


####Readers

#Find forcing files needed based on days:
day_i = startTimes
day_range = [startTime]
while day_i<(endTime + relativedelta(days=1)):
    day_i = day_i + relativedelta(days=1)
    day_range.append(day_i)

i=0
pattern_norkyst=[]
while i < len(day_range)-1:
	day_i = day_range[i]
	day_j = day_range[i+1]
	x='/cluster/work/support/jonal/A11/norfjords_160m_his.nc4_'+str(day_i.year)+str(day_i.month).zfill(2)+str(day_i.day).zfill(2)+'01-'+str(day_j.year)+str(day_j.month).zfill(2)+str(day_j.day).zfill(2)+'00'
	pattern_norkyst.append(x)
	i += 1

#proj = "+proj=stere +ellps=WGS84 +lat_0=90.0 +lat_ts=60.0 +x_0=1848640 +y_0=1432320 +lon_0=70"
reader_norkyst = reader_ROMS_native.Reader(pattern_norkyst)
o.add_reader([reader_norkyst]) 

#Adding readers "lazily"
#o.add_readers_from_list(pattern_norkyst)
       
#Configuration 
#o.set_config('general:use_auto_landmask',False) # Override default landmask
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

lon_m_outer_e = [18.5382232] 
lat_m_outer_e = [69.3079802] 
lon_m_outer_w = [18.5056143] 
lat_m_outer_w = [69.3062551] 



#start_times = [datetime(2018, 4, 1, 0), datetime(2018, 4, 2, 0)] # Seed at specific times
start_times = [startTime + timedelta(days=n) for n in range(0, 14, 1)] # Seed at multiple times
for t in start_times:
    #o.seed_elements(lon=lon_m_inner, lat=lat_m_inner, z=z, time=t, number=N, radius=20, origin_marker=0) 
    #o.seed_elements(lon=lon_m_middle, lat=lat_m_middle, z=z, time=t, number=N, radius=20, origin_marker=1)
    #o.seed_elements(lon=lon_m_outer, lat=lat_m_outer, z=z, time=t, number=N, radius=20, origin_marker=2)
    o.seed_cone(lon=[lon_m_outer_e, lon_m_outer_w], lat=[lat_m_outer_e, lat_m_outer_w], number=N, radius=20,time=t)
            
# Running model
o.run(time_step=3600, end_time=endTime, time_step_output=3600*24, outfile=outfile, export_buffer_length=4)

# Show output
#o.plot(fast=True, linecolor='origin_marker', legend=['Målselv','Aursfjord','Nordfjord'],colorbar=False,filename='drift_plot.png')
#o.plot_property('z')
#o.plot_property('z', mean=True)
#o.animation(fast=True, color='origin_marker', legend=['Målselv','Aursfjord','Nordfjord'],colorbar=False,filename='drift_animation.mp4')
