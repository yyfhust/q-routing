##
# simulator.py
# ---
# Creates a simulation of a network with randomly-generated
# latency and packet drop rates.
##

from simulator import NetworkSimulator

if __name__ == '__main__':
    n_s = NetworkSimulator(100)
    n_s.routePackets(2, verbose=True)
