##
# simulator.py
# ---
# Creates a simulation of a network with randomly-generated
# latency and packet drop rates.
##

from simulator import NetworkSimulator

if __name__ == '__main__':
  nS = NetworkSimulator(100)
  nS.routePackets(1000, verbose = True)
