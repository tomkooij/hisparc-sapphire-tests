# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 11:18:25 2014

@author: Tom
"""
import tables
import sapphire

STATIONS = [501]
START = datetime.datetime(2014,8,1)
END = datetime.datetime(2014,9,1)
FILENAME = 'station_501_augustus2014.h5'



#
# Read event data from the ESD
#  store in table `/sSTATION' for example: /s501
#
def create_new_event_file(filename, stations, start, end):

    print   "creating file: ",filename
    data = tables.open_file(filename,'w')

    print "reading from the ESD"    
    for station in stations:
        print "Now reading station %d" % station
        sapphire.esd.download_data(data, '/s%d' % station, station, START, END)

    return data
    
#
# Open existing coincidence table. 
# Only check if "/coincidences" are in table, no other checks
def open_existing_events_file(filename):
    data = tables.open_file(FILENAME, 'a')
    return data

#
