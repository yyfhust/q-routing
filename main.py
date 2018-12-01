##
# simulator.py
# ---
# Creates a simulation of a network with randomly-generated
# latency and packet drop rates.
##

from simulator import NetworkSimulator
from packetrouter import QPacketRouter, RandomPacketRouter, RIPPacketRouter
from matplotlib import pyplot as plt

def get_averages(total_times, kernel_size):
  return [sum(total_times[i * kernel_size:(i + 1) * kernel_size]) / kernel_size for i in
          range(int(len(total_times) / kernel_size))]

if __name__ == '__main__':
  # network settings
  NUM_NODES = 40
  DROP_NODE_FRACTION = 0.8
  DROP_NODE_CONNECTIVITY = 0.6

  # load simulator
  NUM_PACKETS = 200000
  PACKETS_PER_BATCH = 4000
  DROP_NODES = False

  # for graphing
  KERNEL_SIZE = 2000

  n_s = NetworkSimulator(NUM_NODES, drop_node_fraction=DROP_NODE_FRACTION,
                         drop_node_connectivity=DROP_NODE_CONNECTIVITY)
  q_packet_router = QPacketRouter(n_s)
  rip_packet_router = RIPPacketRouter(n_s)

  test_packets = n_s.generate_packets(NUM_PACKETS)
  kernel_size = KERNEL_SIZE

  print("RIP routing: ")
  n_s.simulate_network_load_parallel(test_packets, rip_packet_router, packets_per_batch=PACKETS_PER_BATCH,
                                     drop_nodes=DROP_NODES, verbose=True)

  total_times = [packet.totalTime for packet in test_packets]
  rip_average_times = get_averages(total_times, kernel_size)

  # reset network
  for packet in test_packets: packet.reset()
  if DROP_NODES:
    n_s.reset_dropped_nodes()

  print("Q-Routing:")
  n_s.simulate_network_load_parallel(test_packets, q_packet_router, packets_per_batch=PACKETS_PER_BATCH,
                                     drop_nodes=DROP_NODES, verbose=True)

  total_times = [packet.totalTime for packet in test_packets]
  q_average_times = get_averages(total_times, kernel_size)

  fig = plt.figure()
  ax1 = fig.add_subplot(111)
  ax1.scatter(range(len(q_average_times)), rip_average_times, label="rip")
  ax1.scatter(range(len(q_average_times)), q_average_times, label="q-routing")
  plt.legend(loc='upper left')
  plt.ylabel("transmission time (ms)")
  plt.xlabel("iteration (100 packets)")
  plt.savefig('rip-vs-qr-no-drop.png', dpi=256)
