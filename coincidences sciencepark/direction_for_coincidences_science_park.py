"""
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
# main ()
#
data = tables.open_file(FILENAME, 'a')

#sapphire.esd.download_coincidences(data,cluster='Aarhus', start=START, end=END, n=N)
#sapphire.esd.download_coincidences(data,stations=STATIONS, start=START, end=END, n=N)


print "************** Results:"
print "number of coincidences in datafile: %i " % data.root.coincidences.coincidences.nrows
results = data.root.coincidences.coincidences
shower_directions = data.root.coincidences.reconstructions

timestamps = results.col("timestamp")
ids = results.col("id")
number_of_events = len(ids) 
print "DEBUG: number of events",number_of_events
#
# Reconstruct (direction) for coincidences
#
#dirrec = ReconstructESDCoincidences(data, overwrite=True)
#dirrec.reconstruct_and_store() 

#for station in STATIONS:
    
#    station_path = '/hisparc/cluster_amsterdam/station_%d' % station
    
    #
    # TODO Handle empty (non-existing) station_id (ie: no data for station in datafile)
    #
#    if data.get_node(station_path+'/events').nrows == 0:    
#        print "empty event list. Skipping"
#    else:        
#    dirrec = ReconstructESDEvents(data, station_path, station, overwrite=True)
#    dirrec.reconstruct_and_store()

# dictionary succes_list[coincidence_id]=aantal succesvol gereconstrueerde losse events
succes_list=dict()

for i in [3]: 

    
    pretty_time = datetime.datetime.fromtimestamp(timestamps[i]).strftime('%d-%m-%Y %H:%M:%S')    
    print " * * * ************************************"    
    print "event number %d at timestamp %d which is %s" % (ids[i], timestamps[i], pretty_time)


    stations_in_this_coincidence = []
  
    #
    # Er is niet voor elke coinc een reconstruction.
    # TODO: zoek echt naar de juist reconstruction behorende bij coincidence
    # 
      
    # get the match row from the table
    direction = shower_directions.read_where('id==i')
    #print direction
    if direction:
        timestamp = direction[0][1]
        zenith = direction[0][5]*180/math.pi
        azimuth = direction[0][6]*180/math.pi
        print "id %d timestamp %d" % (i, timestamp)
        print "Shower: zen azi", zenith, azimuth
    else:
        print "no direction reconstruction in database for this coincidence (shower)"

    
    for station in STATIONS:       
        # check which stations are in coincidence (debugging / crosscheck c_index)
         
        # column "s501" is true if station 501 is in this coincide        
        if results.col("s%d" % station)[i]:       
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

    for station_id,event_id in data.root.coincidences.c_index[i]: 
                       
            
            station_path = data.root.coincidences.s_index[station_id]
            print " *** station %s event_id %s" % (station_path, event_id)           
            event = data.get_node(station_path).reconstructions.read_where('id==event_id')
            if event:            
                timestamp = event[0][1]
                zenith = event[0][5]*180/math.pi
                azimuth = event[0][6]*180/math.pi
                print "id %d timestamp %d" % (i, timestamp)
                print "station: zen azi", zenith, azimuth
                reconstructed_events += 1

            else:
                print "no direction reconstruction in database for this event"
            
    succes_list[i]=reconstructed_events
                
print "****************************************************"
# reverse dictionary blah blah blah
score = invert_dict(succes_list)

#for k in range(5,8):
#    print "Coincidences met %d reconstructed events" % k ,score[k]
    
       
    
data.close() 

