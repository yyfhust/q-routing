from network import NodeAttr, EdgeAttr, Packet
from random import choice
import networkx as nx
from queue import Queue

# every 20 packets, balance load on all edges
LOAD_BALANCE_FREQUENCY = 20


class NetworkSimulator:
  # numNodes : # of nodes in the randomly gen. network
  def __init__(self, numNodes):
    self.G = nx.connected_watts_strogatz_graph(numNodes, 5, 0.8)

    # Generate and associate attributes to node and edges in G.
    self.nodeAttrs = {node : NodeAttr() for node in self.G.nodes}
    self.edgeAttrs = {edge : EdgeAttr() for edge in self.G.edges}


  def getEdgeAttr(self, n1, n2):
    if (n1, n2) in self.edgeAttrs: return self.edgeAttrs[(n1, n2)]
    if (n2, n1) in self.edgeAttrs: return self.edgeAttrs[(n2, n1)]
    return None


  # Route a single packet along an edge, updating its
  # total travel time and whether or not it's been dropped.
  def traverseEdge(self, packet, src, dst):
    # Get most recently traveled node and find the other
    # node in the edge.
    packet.addToPath(dst)
    edgeAttr = self.getEdgeAttr(src, dst)
    edgeAttr.increase_load()
    travelTime = edgeAttr.getTravelTime()
    packet.totalTime += travelTime
    packet.dropped = edgeAttr.isDropped()

    return travelTime


  def generate_packet(self):
    n1 = choice(list(self.G.nodes))
    n2 = choice(list(self.G.nodes))
    while n1 == n2:
      n2 = choice(list(self.G.nodes))
    return Packet(n1, n2)


  def generate_packets(self, n):
    return [self.generate_packet() for _ in range(n)]


  def balance_load(self):
    for edge in self.edgeAttrs.values(): edge.decrease_load()


  #TODO nodes with larger queues have higher latencies?
  def simulate_network_load_parallel(self, packets, packetRouter, verbose = False):
    node_queues = {}
    n = len(packets)
    total_path_length = 0
    dropped_packets = 0
    total_time = 0
    #TODO send packets in batches rather than populating queues all at once
    for i, packet in enumerate(packets):
        packet_src = packet.src
        if packet_src in node_queues:
            node_queues[packet_src].put(packet)
        else:
            node_queues[packet_src] = Queue()
            node_queues[packet_src].put(packet)
    while node_queues:
        # cycle through nodes, processing one packet at each node at  a time
        nodes = list(node_queues.keys())
        for node in nodes:
            queue = node_queues[node]
            packet_to_route = queue.get()
            next_node = packetRouter.routePacketSingleStep(packet_to_route, node)
            if not next_node:
                #packet was dropped
                dropped_packets += 1
                if node_queues[node].empty():
                    del node_queues[node]
                continue
            if next_node == packet_to_route.dst:
                # packet routed successfully
                total_path_length += len(packet_to_route.path)
                total_time += packet_to_route.totalTime
            else: # add next node to appropriate queue
                if next_node in node_queues:
                    node_queues[next_node].put(packet_to_route)
                else:
                    node_queues[next_node] = Queue()
                    node_queues[next_node].put(packet_to_route)
            if node_queues[node].empty():
                del node_queues[node]
        self.balance_load()

    if verbose:
      # Print packet stats for debugging.
      avg_length = total_path_length / (n - dropped_packets)
      avg_time = total_time / (n - dropped_packets)
      print(" avg path length:       %f" % avg_length)
      print(" avg transmission time: %f" % avg_time)
      print(" dropped packets:       %i / %i" % (dropped_packets, n))




  # Generate n packets and simulate a route for all of them.
  def simulate_network_load(self, packets, packetRouter, verbose = False):
    n = len(packets)
    total_path_length = 0
    dropped_packets = 0
    total_time = 0
    for i, packet in enumerate(packets):
      # Generate new packet.
      # TODO: Do we allow packets to go to itself?
      if i % LOAD_BALANCE_FREQUENCY == 0:
        self.balance_load()
      packetRouter.routePacket(packet)
      total_path_length += len(packet.path) / n
      total_time += packet.totalTime / n
      dropped_packets += packet.dropped

    if verbose:
      # Print packet stats for debugging.
      print(" avg path length:       %f" % total_path_length)
      print(" avg transmission time: %f" % total_time)
      print(" dropped packets:       %i / %i" % (dropped_packets, n))
    return 0
