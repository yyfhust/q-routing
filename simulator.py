from network import NodeAttr, EdgeAttr, Packet
from random import shuffle
from random import choice
from random import sample
import numpy as npd
import networkx as nx

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
    travelTime = edgeAttr.getTravelTime()
    packet.totalTime += travelTime
    packet.dropped = edgeAttr.isDropped()

    return travelTime

  # Generate n packets and simulate a route for all of them.
  def simulateNetworkLoad(self, n, packetRouter, verbose = False):
    # TODO: Generate a packet and have it routed thru
    # different nodes, adding to total travel time and
    # if dropped.
    total_path_length = 0
    dropped_packets = 0
    total_time = 0
    for k in range(n):
      # Generate new packet.
      # TODO: Do we allow packets to go to itself?
      n1 = choice(list(self.G.nodes))
      n2 = choice(list(self.G.nodes))
      while n1 == n2:
        n2 = choice(list(self.G.nodes))

      packet = Packet(n1, n2)
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
