import sys
import os

if float(sys.version[0])<3:
    import cPickle as pickle

import datetime

import numpy as np
import netCDF4
import matplotlib.mlab as mp




def get_cstr():
    '''Returns case-string'''
    path = os.getcwd()
    return path.split(os.sep)[-1]
    


class Filelist():
    '''Object linking points in time to files and indices in files (model results)'''

    def __init__(self, name='fileList.txt', start_time=None, stop_time=None, time_format='FVCOM'):
        '''Load information from file. Crop if start or stop is given.'''

        fid=open(name,'r')
        self.time=np.empty(0)
        self.path=[]
        self.index=[]

        for line in fid:
            self.time=np.append(self.time, float(line.split()[0]))
            self.path.append(line.split()[1])
            self.index.append(int(line.split()[2]))

        fid.close()
        
        if time_format == 'FVCOM':
            self.time_units = 'days since 1858-11-17 00:00:00'
        elif time_format == 'WRF':
            self.time_units = 'days since 1948-01-01 00:00:00'
        elif time_format == 'ROMS':
            self.time_units = 'seconds since 1970-01-01 00:00:00'
        elif time_format == 'WRF_dk':
            self.time_units = 'minutes since 1900-01-01 00:00:00'



        self.datetime = netCDF4.num2date(self.time, units = self.time_units)

        self.crop_list(start_time, stop_time)



    def crop_list(self, start_time=None, stop_time=None):
        '''Remove values oustide specified time range.'''
        
        if start_time is not None:

            year = int(start_time.split('-')[0])
            month = int(start_time.split('-')[1])
            day = int(start_time.split('-')[2])
            hour = int(start_time.split('-')[3])
            
            t1 = datetime.datetime(year, month, day, hour)
            ind = np.where(self.datetime >= t1)[0]
            self.time = self.time[ind]
            self.datetime = self.datetime[ind]
            self.path = [self.path[i] for i in list(ind)]
            self.index = [self.index[i] for i in list(ind)]

        if stop_time is not None:

            year = int(stop_time.split('-')[0])
            month = int(stop_time.split('-')[1])
            day = int(stop_time.split('-')[2])
            hour = int(stop_time.split('-')[3])
            t1 = datetime.datetime(year, month, day, hour)
            
            ind = np.where(self.datetime <= t1)[0]
            self.time = self.time[ind]
            self.datetime = self.datetime[ind]
            self.path =  [self.path[i] for i in list(ind)]
            self.index = [self.index[i] for i in list(ind)]



    def find_nearest(self, yyyy, mm, dd, HH=0):
        '''Find index of nearest fileList entry to given point in time.'''
        
        t = datetime.datetime(yyyy, mm, dd, HH)
        fvcom_time = netCDF4.date2num(t, units
                =self.time_units)
        dt = np.abs(self.time - fvcom_time)
        ind = np.argmin(dt)

        return ind

    def write2file(self, name):
        '''Write to file.'''

        fid = open(name, 'w')
        for t, p, i in zip(self.time, self.path, self.index):
            line = str(t) + '\t' + p + '\t' + str(i) + '\n'
            fid.write(line)

        fid.close()


    def unique_files(self):
        '''Find unique files (paths) in fileList.'''
        unique_files = []
        for p in self.path:
            if p not in unique_files:
                unique_files.append(p)
        return unique_files





def load(name):
    '''Load object stored as p-file.'''
    obj = pickle.load(open(name, 'rb'))
    return obj




