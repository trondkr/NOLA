#!/usr/bin/env python

import sys 
sys.path.append('/cluster/home/kristokv/opendrift')
sys.path.append('../opendrift')
import os
from datetime import datetime, timedelta
import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import opendrift
from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_oscillating


startDay='2018-3-1-0'
endDay='2018-3-7-0'
run_name = 'opendrift'
rivers=['Målselv_inner','Målselv_middle','Målselv_outer']
histogram_file = 'runoff_histogram.nc'

outfile = '../results/%s_%s_to_%s.nc'%(run_name,startDay,endDay)

#%%
# Opening the output file lazily with Xarray.
# This will work even if the file is too large to fit in memory, as it
# will read and process data chuck-by-chunk directly from file using Dask.
o = opendrift.open_xarray(outfile)

# Density per pixel summed over origins:
river_water = o.get_histogram(pixelsize_m=1500) # Number of particles per 1500m pixel
rw = river_water.sum(dim='origin_marker') # Sum over all origins
#o.animation(background=do.where(do>0),show_elements=False)

# Total coverage on the last time step:
rwlast = rw[-1]
o.plot(background=rwlast.where(rwlast>0), fast=True, show_particles=False, title='Last timestep-All rivers',filename='figures/lastStepAllRivers_%s_to_%s.png'%(startDay,endDay))

# Cumulative coverage:
rwcum = rw.sum(dim='time')
o.plot(background=rwcum.where(rwcum>0), fast=True, show_particles=False, title='Cumulative-All rivers',filename='figures/cumulativeAllRivers_%s_to_%s.png'%(startDay,endDay))

# Coverage per origin
for x in [0,1,2]:
    rwx = river_water.isel(origin_marker=x)
    rwcumx = rwx.sum(dim='time')
    o.plot(background=rwcumx.where(rwcumx>0), fast=True, show_particles=False, title='Cumulative-%s'%(rivers[x]),filename='figures/cumulative_%s__%s_to_%s.png'%(rivers[x],startDay,endDay))

#%%
# We want to extract timeseries of river water at the coordinates of a hypothetical measuring station
# as well as the amount of river water passing through two defined areas/regions

#%%
# Animation of the spatial density of river runoff water.
# See River Opendrift runoff script for weighing of runoff from different rivers.

#%%
#rw = river_water.isel(origin_marker=1)    # For one of the rivers
river_water.name = 'River water [particles/cell]'

station_lon = 18.39
station_lat = 69.47
box1_lon = [18.33, 18.56]
box1_lat = [69.4, 69.42]
box2_lon = [17.9,18.1]
box2_lat = [69.52, 69.54]

text = [{'s': rivers[0], 'x': 18.25, 'y': 69.26, 'fontsize': 10, 'color': 'g',
         'backgroundcolor': 'white', 'bbox': dict(facecolor='white', alpha=0.6), 'zorder': 1000},
        {'s': rivers[1], 'x': 18.65, 'y': 69.26, 'fontsize': 10, 'color': 'g',
         'backgroundcolor': 'white', 'bbox': dict(facecolor='white', alpha=0.6), 'zorder': 1000},
        {'s': rivers[2], 'x': 19.1, 'y': 69.26, 'fontsize': 10, 'color': 'g',
         'backgroundcolor': 'white', 'bbox': dict(facecolor='white', alpha=0.6), 'zorder': 1000},
        {'s': '* Station', 'x': station_lon, 'y': station_lat, 'fontsize': 10, 'color': 'k',
         'backgroundcolor': 'white', 'bbox': dict(facecolor='none', edgecolor='none', alpha=0.4), 'zorder': 1000}]
box = [{'lon': box1_lon, 'lat': box1_lat, 'text': 'Area 1', 'fc': 'none', 'alpha': 0.8, 'lw': 1, 'ec': 'k'},
       {'lon': box2_lon, 'lat': box2_lat, 'text': 'Area 2', 'fc': 'none', 'alpha': 0.8, 'lw': 1, 'ec': 'k'}]

o.animation(background=rw.where(rw>0), bgalpha=1, fast=False,
            show_elements=False, vmin=0, vmax=120, text=text, box=box,filename='figures/runoffThroughAreas_%s_to_%s.mp4'%(startDay,endDay))


#%%
# Plotting time series of river runoff, and corresponding water passing through the station and the two defined areas/box
first = o.startDay
last = o.endDay
numdays = (last-first).days
times = []
for x in range (0, numdays):
    times.append(first + datetime.timedelta(days=x))


fig, (ax2, ax3, ax4) = plt.subplots(3, 1)
# Area 1
t1 = river_water.sel(lon_bin=slice(box1_lon[0], box1_lon[1]),
                     lat_bin=slice(box1_lat[0], box1_lat[1]))
t1 = t1.sum(('lon_bin', 'lat_bin'))
t1.isel(origin_marker=0).plot(label=rivers[0], ax=ax2)
t1.isel(origin_marker=1).plot(label=rivers[1], ax=ax2)
t1.isel(origin_marker=2).plot(label=rivers[2], ax=ax2)
#t1.sum(dim='origin_marker').plot(label='Total', linestyle='--', ax=ax2)
ax2.set_title('Water particles passing through Area 1')
# Area 2
t2 = river_water.sel(lon_bin=slice(box2_lon[0], box2_lon[1]),
                     lat_bin=slice(box2_lat[0], box2_lat[1]))
t2 = t2.sum(('lon_bin', 'lat_bin'))
t2.isel(origin_marker=0).plot(label=rivers[0], ax=ax3)
t2.isel(origin_marker=1).plot(label=rivers[1], ax=ax3)
t2.isel(origin_marker=2).plot(label=rivers[2], ax=ax3)
#t2.sum(dim='origin_marker').plot(label='Total', linestyle='--', ax=ax3)
ax3.set_title('Water passing through Area 2')
# Extracting time series at the location of the station
t = river_water.sel(lon_bin=station_lon, lat_bin=station_lat, method='nearest')
t.isel(origin_marker=0).plot(label=rivers[0], ax=ax4)
t.isel(origin_marker=1).plot(label=rivers[1], ax=ax4)
t.isel(origin_marker=2).plot(label=rivers[2], ax=ax4)
#t.sum(dim='origin_marker').plot(label='Total', linestyle='--', ax=ax4)
ax4.legend()
ax4.margins(x=0)

for ax in [ax2, ax3, ax4]:
    ax.margins(x=0)
    ax.legend()
    ax.set_xticks([])
    ax.set_xlabel(None)
ax4.set_title('Density of water particles at Station')
ax4.xaxis.set_major_formatter(DateFormatter("%d %b %H"))
#plt.show()
fig.savefig('figures/timeSeriesThroughAres_%s_to_%s.png'%(startDay,endDay))


#%%
# Finally, plot the spatial distribution of mean age of water 
num = o.get_histogram(pixelsize_m=1500, weights=None, density=False)
num.name = 'number'
num.to_netcdf(histogram_file)

mas = o.get_histogram(pixelsize_m=1500, weights=o.ds['age_seconds'], density=False)
mas = mas/(3600*24)  # in daus
mas = mas/num  # per area
mas.name='mean_age'
mas.to_netcdf(histogram_file, 'a')
for x in [0,1,2]:
    #mas = mas.mean(dim='time').sum(dim='origin_marker')  # Mean time of both rivers
    mas_x = mas.mean(dim='time').isel(origin_marker=x)  # Mean age of a single river
    mas_x.name='Mean age of water [days]'
    o.plot(background=mas_x.where(mas_x>0), fast=True, show_particles=False,filename='figures/meanWaterAge_%s_%s_to_%s.png'%(rivers[x],startDay,endDay))


# Cleaning up
os.remove(histogram_file)

# Plots of depth - has to be done with regular file opening
o = opendrift.open(outfile)
#o.animation_profile() # Animation of depth distribution by time/longitude
o.plot_property('z',filename='figures/verticalDistAllParticles_%s_to_%s.png'%(startDay,endDay)) # Depth distribution all particles
o.plot_property('z',mean=True,filename='figures/verticalDistMean_%s_to_%s.png'%(startDay,endDay)) # Mean depth distribution per timestep
o.animate_vertical_distribution(filename='figures/verticalDist_timestep_%s_to_%s.mp4'%(startDay,endDay)) # Distribution in depth over time
#o.plot_vertical_distribution(filename='figures/verticalDist_timestep_%s_to_%s.mp4'%(startDay,endDay)) # Interactive plot with time step, cannot be saved?
