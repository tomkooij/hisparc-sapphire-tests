"""

"""

import tables
import matplotlib.pyplot as plt
import datetime
import sapphire

#import sapphire.clusters

from sapphire.analysis.reconstructions import ReconstructESDEvents

STATIONS = [501, 502, 503, 504, 505, 506, 507, 508, 509]
START = datetime.datetime(2014,9,1)
END = datetime.datetime(2014,9,2)
FILENAME = 'esddata_sciencepark_1sep2014.h5'


def create_and_read_new_ESD_table(name, stations, start, end):

    data = tables.open_file(name, 'w')

    station_groups = ['/s%d' % u for u in STATIONS]
    for stations, group in zip(STATIONS, station_groups):
        print "\nReading ESD for station", stations
        sapphire.esd.download_data(data, group, stations, START, END)

    return data

    
def open_existing_ESD_table(name):

    data = tables.open_file(name, 'a')
    return data

    
def reconstruct_events(data,station):
    station_path = '/s%d' % station
    print "Reconstruction for ", station_path  

    if data.get_node(station_path+'/events').nrows == 0:
        print "empty event table. Skipping"
        return

    if station_path+'/reconstructions/'  not in data:
        dirrec = ReconstructESDEvents(data, station_path, station, overwrite=False)
        dirrec.reconstruct_and_store()
    else:
        print "reconstruction table already in datafile. Skipping."

    

#
# main ()
#

data = create_and_read_new_ESD_table(FILENAME, STATIONS, START, END)
#data = open_existing_ESD_table(FILENAME)

for station in STATIONS:
    reconstruct_events(data, station)

        
results = data.root.s501.reconstructions
plt.figure()
plt.polar(results.col('azimuth'),
                  results.col('zenith'), 'ko', alpha=0.2)

data.close()
