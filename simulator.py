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
    packet.totalTime += edgeAttr.getTravelTime()
    packet.isDropped = edgeAttr.isDropped()
    #TODO: Do something if packet is dropped, i.e. freak the fuck out

  # Route a single packet from packet.src to packet.dst.
  def routePacket(self, packet):
    # TODO: Flag to route packet according to a random policy vs.
    #       according to Q-values.
    cur = packet.src
    while cur != packet.dst:
      neighbors = [n for n in self.G.neighbors(cur)]
      nxt = choice(neighbors)
      self.traverseEdge(packet, cur, nxt)
      cur = nxt

  # Generate n packets and simulate a route for all of them.
  def routePackets(self, n):
    # TODO: Generate a packet and have it routed thru
    # different nodes, adding to total travel time and
    # if dropped.
    for k in range(n):
      # Generate new packet.
      # TODO: Do we allow packets to go to itself?
      n1 = choice(list(self.G.nodes))
      n2 = choice(list(self.G.nodes))
      while (n1 == n2): 
        n2 = choice(list(self.G.nodes))

      packet = Packet(n1, n2)
      self.routePacket(packet)
      break

    return 0

# TODO: Move this elsewhere. Only here for testing.
nS = NetworkSimulator(100)
nS.routePackets(1000)