import sapphire.api

# get the sciencepark cluster station IDs from the network
network = sapphire.api.Network()
stations = network.stations(subcluster=500)

# create a list of station numbers
sciencepark_cluster = [station['number'] for station in stations]
print sciencepark_cluster

# for each station print GPS coordinates
for station in sciencepark_cluster:
    print sapphire.api.Station(station).location()
