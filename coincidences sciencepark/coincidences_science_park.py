"""
coincidences_science_park.py

Reconstrueer richtingen voor coincidences (N>=7 stations) van het Sciece park cluster

gebruikt c_index om losse events van stations aan coincidences te koppelen

"""

import tables
import matplotlib.pyplot as plt
import datetime
import time
import sapphire

from sapphire.analysis.reconstructions import *

STATIONS = [501, 502, 503, 504, 505, 507, 508, 509]
START = datetime.datetime(2014,8,1)
END = datetime.datetime(2014,9,1)
FILENAME = 'coinc_sciencepark_aug2014.h5'
N = 7

# uit think python par 11.4
# draai een dict om
def invert_dict(d):
    inverse = dict()
    for key in d:
        val = d[key]
        if val not in inverse:
            inverse[val] = [key]
        else:
            inverse[val].append(key)
    return inverse






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
        zenith = direction[0][5]*180/math.pi
        azimuth = direction[0][6]*180/math.pi
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
                zenith = event[0][5]*180/math.pi
                azimuth = event[0][6]*180/math.pi
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
    return reconstructed_events
    

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

coincidence_id = 3

print "*** "
print "selected event number ", id
print "***"

for coincidence_id in range(number_of_events):
    reconstructed_events = gather_event_data_for_coincidence(data, coincidence_id, STATIONS)
    print "number of reconstructed events in coincidence", reconstructed_events
    
#print event_data


    
                
print "****************************************************"
# reverse dictionary blah blah blah
#score = invert_dict(succes_list)

#for k in range(5,8):
#    print "Coincidences met %d reconstructed events" % k ,score[k]
    
       
    
data.close() 

