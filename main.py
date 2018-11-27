##
# simulator.py
# ---
# Creates a simulation of a network with randomly-generated
# latency and packet drop rates.
##

from simulator import NetworkSimulator
from packetrouter import QPacketRouter, RandomPacketRouter, RIPPacketRouter
import networkx as nx

if __name__ == '__main__':
  NUM_NODES = 25
  NUM_PACKETS = 5000000

  n_s = NetworkSimulator(NUM_NODES)
  q_packet_router = QPacketRouter(n_s)
  rip_packet_router = RIPPacketRouter(n_s)
  random_packet_router = RandomPacketRouter(n_s)

  # Sequential routing
  '''
  test_packets = n_s.generate_packets(NUM_PACKETS)

  print("RIP routing: ")

  n_s.simulate_network_load(test_packets, rip_packet_router, verbose=True)

  test_packets = n_s.generate_packets(NUM_PACKETS)

  print("Q-Routing:")
  n_s.simulate_network_load(test_packets, q_packet_router, verbose=True)
  '''

  # Parallel routing
  test_packets = n_s.generate_packets(NUM_PACKETS)
  print("RIP routing: ")
  n_s.simulate_network_load_parallel(test_packets, rip_packet_router, verbose=True)

  test_packets = n_s.generate_packets(NUM_PACKETS)
  print("Q-Routing:")
  n_s.simulate_network_load_parallel(test_packets, q_packet_router, verbose=True)
