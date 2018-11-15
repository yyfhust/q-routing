##
# simulator.py
# ---
# Creates a simulation of a network with randomly-generated
# latency and packet drop rates.
##

from simulator import NetworkSimulator

if __name__ == '__main__':
    networkSimulator = NetworkSimulator(numNodes = 10, numEdges = 4)
    networkSimulator.routePackets(n = 1000)
