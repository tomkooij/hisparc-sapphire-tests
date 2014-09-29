"""
coincidences_science_park.py

Reconstrueer richtingen voor coincidences (N>=7 stations) van het Sciece park cluster

gebruikt c_index om losse events van stations aan coincidences te koppelen

"""

from visual import *

import tables
import matplotlib.pyplot as plt
import datetime
import time
import sapphire
import sapphire.api
import sapphire.clusters

from sapphire.analysis.reconstructions import *

# interesting coincidence 3, 149 (many vectors)
#    153 is awkward
#    135  zenith angle of 35 degres and multiple vectors
#    111  zenith angle 50 degrees (single vector)

INTERESTING_COINCIDENCE = 135

STATIONS = [501, 502, 503, 504, 505, 507, 508, 509]
START = datetime.datetime(2014,8,1)
END = datetime.datetime(2014,9,1)
FILENAME = 'coinc_sciencepark_aug2014.h5'
N = 7



#
# Read coincidence data from the ESD (slow!)
#
def create_new_coincidence_file(filename,stations, start, end, n):

    print   "creating file: ",filename
    data = tables.open_file(filename,'w')

    print "reading from the ESD"    
    sapphire.esd.download_coincidences(data,stations=STATIONS, start=START, end=END, n=N)

    return data
    
#
# Open existing coincidence table. 
# Only check if "/coincidences" are in table, no other checks
def open_existing_coincidence_file(filename):
    data = tables.open_file(FILENAME, 'a')
    assert "/coincidences" in data    
    return data

#
# Reconstruct (direction) for coincidences AND corresponding events
#
def reconstruct_directions(data, stations):   
    dirrec = ReconstructESDCoincidences(data, overwrite=True)
    dirrec.reconstruct_and_store() 

    for station in STATIONS:
    
        station_path = '/hisparc/cluster_amsterdam/station_%d' % station
        print "Now reconstruction single events for ", station
        #
        # TODO Handle empty (non-existing) station_id (ie: no data for station in datafile)
        #
        if data.get_node(station_path+'/events').nrows == 0:    
            print "empty event list. Skipping"
        else:        
            dirrec = ReconstructESDEvents(data, station_path, station, overwrite=True)
            dirrec.reconstruct_and_store()

def gather_event_data_for_coincidence(data, coinc_id, stations):

    results = data.root.coincidences.coincidences
    shower_directions = data.root.coincidences.reconstructions
    timestamps = results.col("timestamp")
   
    event_data = dict()
      
    pretty_time = datetime.datetime.fromtimestamp(timestamps[coinc_id]).strftime('%d-%m-%Y %H:%M:%S')    
    print " * * * ************************************"    
    print "event number %d at timestamp %d which is %s" % (results.col("id")[coinc_id], timestamps[coinc_id], pretty_time)


    stations_in_this_coincidence = []
  
    #
    # Er is niet voor elke coinc een reconstruction.
    # 
      
    # get the match row from the table
    direction = shower_directions.read_where('id==coinc_id')
#    print direction

    if direction:
        timestamp = direction[0][1]
        zenith = direction[0][5]
        azimuth = direction[0][6]
        print "id %d timestamp %d" % (coinc_id, timestamp)
        print "Shower: zen azi", zenith, azimuth

        # should be cluster number. 500 hardcoded
        #
        event_data['500'] = [timestamp, zenith, azimuth]
                
    else:
        print "no direction reconstruction in database for this coincidence (shower)"

    
    for station in stations:       
        # check which stations are in coincidence (debugging / crosscheck c_index)
         
        # column "s501" is true if station 501 is in this coincide        
        if results.col("s%d" % station)[coinc_id]:       
            #print "DEBUG: station ", station, " in coincidence "                     
            #print "DEBUG: index",i            
            stations_in_this_coincidence.append(station)        
    
    print " *** stations in this coincidence ", stations_in_this_coincidence

    #
    # c_index is een lijst met getallenparen: eerste getal is de index van het station
    #   voor s_index. tweede getal is het id uit de bijbehorende eventtable van dat station
    #


    # hou bij hoeveel losse events gereconstrueerd zijn (richting data hebben)
    #  in deze coincidence    
    reconstructed_events = 0

    for station_id,event_id in data.root.coincidences.c_index[coinc_id]: 
                       
            
            station_path = data.root.coincidences.s_index[station_id]
            print " *** station %s event_id %s" % (station_path, event_id)           
            event = data.get_node(station_path).reconstructions.read_where('id==event_id')
            if event:            
                timestamp = event[0][1]
                zenith = event[0][5]
                azimuth = event[0][6]
                print "id %d timestamp %d" % (coinc_id, timestamp)
                print "station: zen azi", zenith, azimuth
                reconstructed_events += 1

                ### store in event_data
                # station_paht = /hisparc/cluster/.../station_501
                # station_path[-3:] = 501 (last three digits)
                # DOES NOT WORK FOR 70000 stations etc
                event_data['%s' % station_path[-3:] ] = [timestamp, zenith, azimuth]
                
            else:
                print "no direction reconstruction in database for this event"
    
    #
    # returns the number of reconstructed events found for this coincidence
    #        
    return event_data
    
#
# This is from sapphire/scripts/scienepark/
# 
def sciencepark_stations():
    network = sapphire.api.Network()
    stations = network.stations(subcluster=500)
    return [station['number'] for station in stations]


def get_cluster(stations):
    cluster = sapphire.clusters.ScienceParkCluster(stations=stations)
    return cluster


def plot_cluster(cluster):
    # Draw detector locations on a map  
    # locations are in meters relative to the cluster center

    # background plane
    # needs OSM map!
    bitmap = materials.loadTGA("ScienceParkMap1024")
    tgrid = materials.texture(data=bitmap,
                          mapping="rectangular",
                          interpolate=False)
    ground = box(pos=(0,0,0),axis=(0,0,1), length=1, height=400, width=700, material=tgrid)
#    ground.rotate(angle=math.pi,axis=(0,0,1))
    
    for station in cluster.stations:
        for i, detector in enumerate(station.detectors):
            detector_x, detector_y = detector.get_xy_coordinates()
                
            # plot a detector as a blue sphere (this avoids tricky directions)    
            sphere(pos=(detector_x, detector_y,2),color=color.red,radius=5)
            
# unused        
        station_x, station_y, station_a = station.get_xyalpha_coordinates()
        print "Plotting station", station.number,station_x, station_y   





#
# main ()
#
#data=create_new_coincidence_file(STATIONS, START, END, END)
data = open_existing_coincidence_file(FILENAME)

# check if direction reconstruction is already present / done
#
# A more thorough way would be to check reconstructions for each station is data
#
if "/coincidences/reconstructions" not in data:
    print "Direction reconstructions not in data. Reconstructing..."
    reconstruct_directions(data,stations)
else:
    print "Direction reconstructions found in data. Skipping"


print "************** Results:"
print "number of coincidences in datafile: %i " % data.root.coincidences.coincidences.nrows

results = data.root.coincidences.coincidences
number_of_events = len(results.col("id")) 
#print "DEBUG: number of events",number_of_events


# select coincidence to plot
coincidence_id = INTERESTING_COINCIDENCE

print "*** "
print "selected event number ", id
print "***"
event_data = gather_event_data_for_coincidence(data, coincidence_id, STATIONS)
#print event_data

#
# close data file before doing the VPython stuff
#
data.close() 


scene = display(title='SciencePark coincidence # %s' % coincidence_id,
     x=0, y=0, width=600, height=400,
     center=(0,0,0), background=(0.53,0.81,1.))


#stations = sciencepark_stations() 
stations = [501, 502, 503, 504, 505, 506, 507, 508, 509]
# plot the science cluster stations (detectors)
cluster = get_cluster(stations)
plot_cluster(cluster)

#
# Big arrow for "direction" of coincidence 
#
coincidence_data = event_data['500']
print coincidence_data
zenith = coincidence_data[1]
azimuth = coincidence_data[2]
arrow(pos=(0,0,0),axis=(math.sin(zenith)*math.cos(azimuth),math.sin(zenith)*math.sin(azimuth),math.cos(zenith)),length=250,shaftwidth=10,color=color.white) 


#
# Yellow arrow for each station (that has direction data)
#    Note: Station can be in coincidence without direction data available
#
# TODO: Visualise which stations are in coincidence (different color?)
for station in cluster.stations:
      
    if str(station.number) in event_data:    
        print "Now drawing incident vector at station:", station.number        
        this_event = event_data['%s' % station.number]
        print this_event
        zenith = this_event[1]
        azimuth = this_event[2]
        
        station_x, station_y, station_a = station.get_xyalpha_coordinates()
    
        arrow(pos=(station_x,station_y,0),axis=(math.sin(zenith)*math.cos(azimuth),math.sin(zenith)*math.sin(azimuth),math.cos(zenith)),length=150,shaftwidth=3,color=color.yellow)
        

dt = 0.01
while 1:
      rate(100)
       
    

