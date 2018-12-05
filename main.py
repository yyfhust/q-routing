##
# simulator.py
# ---
# Creates a simulation of a network with randomly-generated
# latency and packet drop rates.
##

from simulator import NetworkSimulator
from packetrouter import QPacketRouter, HybridRIPQPacketRouter, RandomPacketRouter, RIPPacketRouter
from matplotlib import pyplot as plt
import util as Util

if __name__ == '__main__':
  # network settings
  NUM_NODES = 80
  DROP_NODE_FRACTION = 0.75
  DROP_NODE_CONNECTIVITY = 0.4

  # load simulator
  NUM_PACKETS = 200000
  PACKETS_PER_BATCH = 2000
  DROP_NODES = False

  # for graphing
  KERNEL_SIZE = 2000

  n_s = NetworkSimulator(NUM_NODES, drop_node_fraction=DROP_NODE_FRACTION, drop_node_connectivity=DROP_NODE_CONNECTIVITY)

  # Initialize all packet routers.
  routers = {
    'RIP Router' : RIPPacketRouter(n_s),
    # 'Q-Routing w/ RIP Hybrid' : HybridRIPQPacketRouter(n_s, NUM_NODES, penalize_drops = True),
    'Q Routing w/ Drop Penalization' : QPacketRouter(n_s, penalize_drops = True),
    'Vanilla Q Routing' : QPacketRouter(n_s),
  }
  test_packets = n_s.generate_packets(NUM_PACKETS)

  # Runs n_s.simulate_network_load_parallel() for each router in routers.
  times = Util.simulate_packet_routing(n_s, routers, test_packets, KERNEL_SIZE, PACKETS_PER_BATCH, DROP_NODES)
  Util.plot_times(times, KERNEL_SIZE)
