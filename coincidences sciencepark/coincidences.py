import datetime

import tables

from sapphire.publicdb import download_data
from sapphire.analysis import coincidences
from sapphire.analysis import direction_reconstruction
import sapphire.clusters

STATIONS = [501, 502, 503]
#START = datetime.datetime.today()
#END = START - datetime.timedelta(days=1)
START = datetime.datetime(2014, 8, 7)
END = datetime.datetime(2014, 8, 8)


station_groups = ['/s%d' % u for u in STATIONS]

data = tables.open_file('data_ESDaug7.h5', 'a')
for station, group in zip(STATIONS, station_groups):
    download_data(data, group, station, START, END)
data.close()

""" 
#coin = coincidences.Coincidences(data, '/coincidences', station_groups)
#coin.search_and_store_coincidences()

coinc = data.root.coincidences
#vind events met 8 coincidences
#n = coinc.col('N')   
#for i in range(0,len(n)):
#    if n[i]==8: 
#        print i, coinc[i]

stations = sciencepark_stations() 
cluster = sapphire.clusters.ScienceParkCluster(stations)

data.root.coincidences._v_attrs.cluster = cluster
    
direction = direction_reconstruction.DirectCoincidenceReconstruction(cluster)
direction.reconstruct_angles(coinc) 
data.close()
"""