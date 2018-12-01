from network import NodeAttr, EdgeAttr, Packet
import random
import networkx as nx
from collections import deque

# every 20 packets, balance load on all edges
LOAD_BALANCE_FREQUENCY = 20


class NetworkSimulator:
  # numNodes : # of nodes in the randomly gen. network
  def __init__(self, num_nodes, drop_node_fraction=0.2, drop_node_connectivity=0.5):
    num_drop_nodes = int(num_nodes * drop_node_fraction)
    num_constant_nodes = num_nodes - num_drop_nodes
    self.G = nx.connected_watts_strogatz_graph(num_constant_nodes, 3, 0.9)
    self.constant_nodes = list(self.G.nodes)
    self.generate_drop_nodes(num_drop_nodes, drop_node_connectivity)
    self.nodes_to_drop = list(set(self.G.nodes) - set(self.constant_nodes))
    self.dropped_nodes = []

    # Generate and associate attributes to node and edges in G.
    self.node_attrs = {node : NodeAttr() for node in self.G.nodes}
    self.edge_attrs = {edge : EdgeAttr() for edge in self.G.edges}

  def generate_drop_nodes(self, num_drop_nodes, drop_node_connectivity):
    num_constant_nodes = len(self.G.nodes)
    self.drop_edges = []
    self.nodes_to_drop = []
    self.dropped_nodes = []
    for i in range(num_drop_nodes):
      node_id = chr(i + ord('a'))
      neighbours = random.sample(range(num_constant_nodes), int(num_constant_nodes * drop_node_connectivity))
      self.G.add_node(node_id)
      self.nodes_to_drop.append(node_id)
      edges = [(node_id, x) for x in neighbours]
      self.G.add_edges_from(edges)
      self.drop_edges += edges

  def drop_node(self):
    if self.nodes_to_drop:
      n = random.choice(self.nodes_to_drop)
      self.G.remove_node(n)
      self.nodes_to_drop.remove(n)

  def reset_dropped_nodes(self):
    self.G.add_nodes_from(self.dropped_nodes)
    self.nodes_to_drop = self.nodes_to_drop + self.dropped_nodes
    self.dropped_nodes = []
    self.G.add_edges_from(self.drop_edges)

  def get_edge_attr(self, n1, n2):
    if (n1, n2) in self.edge_attrs: return self.edge_attrs[(n1, n2)]
    if (n2, n1) in self.edge_attrs: return self.edge_attrs[(n2, n1)]
    return None

  # Route a single packet along an edge, updating its
  # total travel time and whether or not it's been dropped.
  def traverseEdge(self, packet, src, dst):
    # Get most recently traveled node and find the other
    # node in the edge.
    packet.addToPath(dst)
    edgeAttr = self.get_edge_attr(src, dst)
    edgeAttr.increase_load()
    travelTime = edgeAttr.getTravelTime()
    packet.totalTime += travelTime
    packet.dropped = edgeAttr.isDropped()

    return travelTime

  def generate_packet(self):
    n1 = random.choice(self.constant_nodes)
    n2 = random.choice(self.constant_nodes)
    while n1 == n2:
      n2 = random.choice(self.constant_nodes)
    return Packet(n1, n2)

  def generate_packets(self, n):
    return [self.generate_packet() for _ in range(n)]

  def balance_load(self):
    for edge in self.edge_attrs.values(): edge.decrease_load()

  def print_load_results(self, n, total_path_length, dropped_packets, total_time):
    # Print packet stats for debugging.
    avg_length = total_path_length / n
    avg_time = total_time / n
    print(" avg path length:       %f" % avg_length)
    print(" avg transmission time: %f" % avg_time)
    print(" dropped packets:       %i / %i" % (dropped_packets, n))

  # iterate through node queues and propagate packets through the network
  def propagate_packets(self, packet_router, node_queues, total_path_length, dropped_packets, total_time):
    # cycle through nodes, processing one packet at each node at  a time
    nodes = list(node_queues.keys())
    for node in nodes:
      queue = node_queues[node]
      packet_to_route = queue.popleft()
      next_node = packet_router.routePacketSingleStep(packet_to_route, node)
      if next_node is None:
        # packet was dropped
        dropped_packets += 1
        next_node = packet_to_route.src
        total_time += packet_to_route.totalTime
        packet_to_route.reset()
      if next_node == packet_to_route.dst:
        # packet routed successfully
        total_path_length += len(packet_to_route.path)
        total_time += packet_to_route.totalTime
      else:  # add next node to appropriate queue
        if next_node in node_queues:
          node_queues[next_node].append(packet_to_route)
        else:
          node_queues[next_node] = deque([packet_to_route])
      if not node_queues[node]:
        del node_queues[node]
    return total_path_length, dropped_packets, total_time

  def send_packets(self, node_queues, packets, packet_index, packets_per_batch):
    for index in range(packet_index, min(packet_index + packets_per_batch, len(packets))):
      packet = packets[index]
      packet_src = packet.src
      if packet_src in node_queues:
        node_queues[packet_src].append(packet)
      else:
        node_queues[packet_src] = deque([packet])
    return packet_index + packets_per_batch

  # TODO nodes with larger queues have higher latencies?
  def simulate_network_load_parallel(self, packets, packet_router,
                                     packets_per_batch=5000,
                                     drop_nodes=False, verbose=False):
    node_queues = {}
    total_path_length, dropped_packets, total_time, packet_index = 0, 0, 0, 0
    while node_queues or packet_index < len(packets):
      # if packets have been routed, send out another batch
      if not node_queues:
        if drop_nodes:
          self.drop_node()
        packet_index = self.send_packets(node_queues, packets, packet_index, packets_per_batch)
      total_path_length, dropped_packets, total_time = self.propagate_packets(packet_router, node_queues,
                                                                              total_path_length, dropped_packets,
                                                                              total_time)
      self.balance_load()
    if verbose:
      self.print_load_results(len(packets), total_path_length, dropped_packets, total_time)

  # Generate n packets and simulate a route for all of them.
  def simulate_network_load(self, packets, packetRouter, verbose = False):
    n = len(packets)
    total_path_length = 0
    dropped_packets = 0
    total_time = 0
    for i, packet in enumerate(packets):
      # Generate new packet.
      if i % LOAD_BALANCE_FREQUENCY == 0:
        self.balance_load()
      packetRouter.routePacket(packet)
      total_path_length += len(packet.path) / n
      total_time += packet.totalTime / n
      dropped_packets += packet.dropped

    if verbose:
      # Print packet stats for debugging.
      #TODO should path length be counted if the packet is dropped? check are these stats right
      print(" avg path length:       %f" % total_path_length)
      print(" avg transmission time: %f" % total_time)
      print(" dropped packets:       %i / %i" % (dropped_packets, n))
    return 0
