##
# simulator.py
# ---
# Creates a simulation of a network with randomly-generated
# latency and packet drop rates.
##

from simulator import NetworkSimulator
from packetrouter import QPacketRouter, RandomPacketRouter
from matplotlib import pyplot as plt

if __name__ == '__main__':
  NUM_NODES = 30
  NUM_PACKETS = 1000

  n_s = NetworkSimulator(NUM_NODES)
  q_packet_router = QPacketRouter(n_s)
  random_packet_router = RandomPacketRouter(n_s)

  test_packets = n_s.generate_packets(NUM_PACKETS)

  print("Random routing: ")
  n_s.simulate_network_load(test_packets, random_packet_router, verbose=True)

  test_packets = n_s.generate_packets(NUM_PACKETS)

  print("Q-Routing:")
  n_s.simulate_network_load(test_packets, q_packet_router, verbose=True)
  plt.scatter(range(NUM_PACKETS), [packet.totalTime for packet in test_packets])
