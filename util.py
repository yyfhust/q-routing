from matplotlib import pyplot as plt

def get_averages(total_times, kernel_size):
  return [sum(total_times[i * kernel_size:(i + 1) * kernel_size]) / kernel_size for i in
          range(int(len(total_times) / kernel_size))]

# TODO: Move this into simulator or packet router.
def simulate_packet_routing(n_s, routers, test_packets, kernel_size, packets_per_batch, drop_nodes):
  times = {}
  
  for name, router in routers.items():
    print("%s: " % name)
    n_s.simulate_network_load_parallel(test_packets, router, packets_per_batch=packets_per_batch, drop_nodes=drop_nodes, verbose=True)

    total_times = [packet.totalTime for packet in test_packets]
    times[name] = get_averages(total_times, kernel_size)

    # Reset network after simulation.
    for packet in test_packets: packet.reset()
    if drop_nodes:
      n_s.reset_dropped_nodes()
  
  return times

def plot_times(times):
  fig = plt.figure()
  ax1 = fig.add_subplot(111)

  for name, time in times.items():   
    ax1.scatter(range(len(time)), time, label=name)

  plt.legend(loc='upper left')
  plt.ylabel("transmission time (ms)")
  plt.xlabel("iteration (100 packets)")
  plt.savefig('rip-vs-qr-no-drop.png', dpi=256)