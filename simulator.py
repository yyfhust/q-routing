from network import NodeAttr, EdgeAttr, Packet
import random
import networkx as nx
from collections import deque
import copy
from copy import deepcopy
 
# every 20 packets, balance load on all edges
LOAD_BALANCE_FREQUENCY = 20
MAX_TIME_OUT = 4000

class NetworkStats:
  def __init__(self):
    self.total_path_length = 0.
    self.total_time = 0.
    self.timed_out_packets = 0.
    self.dropped_packets = 0.
 
class NetworkSimulator:
  # numNodes : # of nodes in the randomly gen. network
  def __init__(self, num_nodes, drop_node_fraction=0.2, drop_node_connectivity=0.5):
    num_drop_nodes = int(num_nodes * drop_node_fraction)
    num_constant_nodes = num_nodes - num_drop_nodes
    self.G = nx.connected_watts_strogatz_graph(num_constant_nodes, 3, 0.9)
    self.constant_nodes = list(self.G.nodes)
    self.generate_droppable_nodes(num_drop_nodes, drop_node_connectivity)
 
    # TODO: Set these as reference just to ensure we reset properly.
    #       May not be most elegant, but guarantees proper reset.
    self.ref_G = self.G.copy()
    self.ref_droppable_nodes = copy.deepcopy(self.droppable_nodes)
 
    # Generate and associate attributes to node and edges in G.
    self.node_attrs = {node : NodeAttr() for node in self.G.nodes}
    self.edge_attrs = {edge : EdgeAttr() for edge in self.G.edges}

    # Node queues, requires reset after simulation
    self.node_queues = {}
 
  def reset(self):
    for edge, edge_attr in self.edge_attrs.items():
      edge_attr.reset()
 
    # Reset graph and droppable_nodes.
    self.G = self.ref_G.copy()
    self.droppable_nodes = copy.deepcopy(self.ref_droppable_nodes)

    # Reset node packet queues
    self.node_queues = {}

 
  def generate_droppable_nodes(self, num_drop_nodes, drop_node_connectivity):
    num_constant_nodes = len(self.G.nodes)
    self.droppable_nodes = []
    for i in range(num_drop_nodes):
      node_id = chr(i + ord('a'))
 
      # Create node and add it to droppable_nodes.
      self.G.add_node(node_id)
      self.droppable_nodes.append(node_id)
 
      # Sample nodes from nodes that aren't droppable and connect them
      # to the newly added droppable node.
      neighbours = random.sample(range(num_constant_nodes), int(num_constant_nodes * drop_node_connectivity))
      self.G.add_edges_from([(node_id, x) for x in neighbours])
 
  def drop_node(self):
    if self.droppable_nodes:
      n = random.choice(self.droppable_nodes)
      self.G.remove_node(n)
      self.droppable_nodes.remove(n)
 
  def get_edge_attr(self, n1, n2):
    if (n1, n2) in self.edge_attrs: return self.edge_attrs[(n1, n2)]
    if (n2, n1) in self.edge_attrs: return self.edge_attrs[(n2, n1)]
    return None
 
  # Route a single packet along an edge, updating its
  # total travel time and whether or not it's been dropped.
  def traverseEdge(self, packet, src, dst):
    # Get most recently traveled node and find the other
    # node in the edge.
    assert((src, dst) in self.G.edges or (dst, src) in self.G.edges)
    packet.addToPath(dst)

    dstNodeAttr = self.node_attrs[dst]
    edgeAttr = self.get_edge_attr(src, dst)
    edgeAttr.increase_load()
    travelTime = edgeAttr.getTravelTime()
    packet.totalTime += travelTime
    packet.totalTime += dstNodeAttr.packet_queue_time * len(self.node_queues.get(dst, []))
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
 
  def print_load_results(self, n, network_stats):
    # Print packet stats for debugging.
    avg_length = network_stats.total_path_length / n
    avg_time = network_stats.total_time / n
    print(" avg path length:       %f" % avg_length)
    print(" avg transmission time: %f" % avg_time)
    print(" timed out packets:     %i / %i" % (network_stats.timed_out_packets, n))
    print(" dropped packets:       %i / %i" % (network_stats.dropped_packets, n))
 
  # Iterate through node queues and propagate packets through the network.
  def propagate_packets(self, packet_router, network_stats):
    # Cycle through nodes, processing one packet at each node at a time.
    nodes = list(self.node_queues.keys())
    for node in nodes:
      # Pop a node from the queue to process its packets.
      queue = self.node_queues[node]
      packet_to_route = queue.popleft()
      if not self.node_queues[node]: del self.node_queues[node]

      next_node = packet_router.routePacketSingleStep(packet_to_route, node)

      # Stop propogating packets if they are timed out.
      if packet_to_route.totalTime > MAX_TIME_OUT:
        network_stats.total_time += packet_to_route.totalTime
        network_stats.timed_out_packets += 1
        continue
 
      # Reroute packet to beginning if packet was dropped.
      if next_node is None:
        network_stats.dropped_packets += 1
        next_node = packet_to_route.src
        # TODO: I've changed it so that travelTime persists across iterations
        #       even when the packet is dropped (this way points are plotted more
        #       accurately). We can revert if resetting was intended behavior.
        packet_to_route.reset(totalTime = packet_to_route.totalTime)
 
      # Handle the next node.
      if next_node == packet_to_route.dst:
        # Packet routed successfully to dst.
        network_stats.total_path_length += len(packet_to_route.path)
        network_stats.total_time += packet_to_route.totalTime
      else:
        # Add next node to appropriate queue.
        if next_node not in self.node_queues: self.node_queues[next_node] = deque()
        self.node_queues[next_node].append(packet_to_route)

    return network_stats
 
  # Sends out a new batch of packets.
  def send_packets(self, packets, packet_index, packets_per_batch):
    for index in range(packet_index, min(packet_index + packets_per_batch, len(packets))):
      packet = packets[index]
      if packet.src not in self.node_queues: self.node_queues[packet.src] = deque()
      self.node_queues[packet.src].append(packet)
 
    return packet_index + packets_per_batch
 
  # TODO nodes with larger queues have higher latencies?
  def simulate_network_load_parallel(self, packets, packet_router,
                                     packets_per_batch=5000,
                                     drop_nodes=False, verbose=False):
    network_stats = NetworkStats()
    packet_index = 0

    # Process batches of packets at a time.
    while self.node_queues or packet_index < len(packets):
      # If packets have been routed, send out another batch.
      if not self.node_queues:
        if drop_nodes: self.drop_node()
        packet_index = self.send_packets(packets, packet_index, packets_per_batch)
 
      network_stats = self.propagate_packets(packet_router, network_stats)
      self.balance_load()
    if verbose:
      self.print_load_results(len(packets), network_stats)
