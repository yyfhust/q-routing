##
# simulator.py
# ---
# Creates a simulation of a network with randomly-generated
# latency and packet drop rates.
##

from simulator import NetworkSimulator
from packetrouter import QPacketRouter, RandomPacketRouter

if __name__ == '__main__':
  n_s = NetworkSimulator(20)
  q_packet_router = QPacketRouter(n_s)
  random_packet_router = RandomPacketRouter(n_s)

  num_test_packets = 10000

  print("Random routing: ")
  n_s.simulateNetworkLoad(num_test_packets, random_packet_router, verbose=True)

  print("Q-Routing:")
  n_s.simulateNetworkLoad(num_test_packets, q_packet_router, verbose=True)