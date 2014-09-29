"""
Science park in VPython
Based on sapphire/scripts/sciencepark/detector_locations.py

"""

from visual import *

import numpy as np

import sapphire.api
import sapphire.clusters
import sapphire.simulations
#from sapphire.simulations.ldf import KascadeLdf


DETECTOR_COLORS = ['black', 'r', 'g', 'b']


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
    
    box(pos=(0,0,0),axis=(0,0,1), length=1, height=400, width=700,color=color.blue)
    
    for station in cluster.stations:
        for i, detector in enumerate(station.detectors):
            detector_x, detector_y = detector.get_xy_coordinates()
                
            # plot a detector as a blue sphere (this avoids tricky directions)    
            sphere(pos=(detector_x, detector_y,2),color=color.red,radius=5)
            
# unused        
        station_x, station_y, station_a = station.get_xyalpha_coordinates()
        print "station", station_x, station_y   



if __name__=="__main__":
    stations = [501,502,503,504,505,506,507,508,509]
    cluster = get_cluster(stations)
    plot_cluster(cluster)

    zenith = 1.843/180*math.pi
    azimuth = 87.261/180*math.pi
    
    axis_x = math.cos(azimuth)
    print axis_x
    
    #plot incident ray for coincidence 1407273686597371847
    arrow(pos=(0,0,0),axis=(0,1,1), length=-100,shaftwidth=3) 
          
          #axis=(math.sin(azimuth),math.cos(azimuth),math.cos(zenith)), shaftwidth=1))

    dt = 0.01
    while 1:
        rate(100)
#    plot_scintillators_in_cluster(cluster)