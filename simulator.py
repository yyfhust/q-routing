from network import Node, Edge, Packet
from random import shuffle
import numpy as npd
import random as rnd

class NetworkSimulator:
  # numNodes : # of nodes in the randomly gen. network
  # numEdges : # of edges in the randomly gen. network
  def __init__(self, numNodes, numEdges):
    self.numNodes = numNodes
    self.numEdges = numEdges
    self.packets = []
    avgEdgesPerNode = min(1, numEdges / numNodes)

    self.nodes = []
    self.edges = set()

    # Randomly generate a connected graph with numNodes nodes
    # and numEdges edges.
    node = Node(0)
    self.nodes.append(node)

    for i in range(1, numNodes):
      n1 = Node(i)

      # Connect node to some n # of nodes already in self.nodes.
      # Randomly generate number of nodes to connect.
      numNodeEdges = avgEdgesPerNode
      for j in range(min(len(self.nodes), numNodeEdges)):
        n2 = rnd.choice(self.nodes)
        while ((n1, n2) in self.edges): n2 = rnd.choice(self.nodes)

        edge = Edge(n1, n2)

      self.nodes.append(n1)

    # Check if we have enough edges. If not, then add edges
    # until we have enough edges.
    # TODO: Hacky and redundant code. Can conslidate.
    for i in range(numEdges - len(self.edges)):
      n1 = rnd.choice(self.nodes)
      n2 = rnd.choice(self.nodes)

      # Avoid self loops and double
      while (n1 == n2): n2 = rnd.choice(self.nodes)
      # Avoid double edges.
      while ((n1, n2) in self.edges): n2 = rnd.choice(self.nodes)

      edge = Edge(n1, n2)
      self.edges.add(edge)

  # TODO: Save network node and edge configurations into a file.
  def writeConfig(self):
    return

  # TODO: Load network node and edge configurations from a file.
  def readConfig(self):
    return

  # Route a single packet along an edge, updating its
  # total travel time and whether or not it's been dropped.
  def traverseEdge(self, packet, edge):
    # Get most recently traveled node and find the other
    # node in the edge.
    n1 = packet.getMostRecentNode()
    n2 = edge.n2 if n1 == edge.n1 else n1

    packet.addToPath(n2)
    packet.totalTime += edge.getTravelTime()
    packet.isDropped = edge.isDropped()
    #TODO: Do something if packet is dropped, i.e. freak the fuck out

    return n2

  # Route a single packet from packet.src to packet.dst.
  def routePacket(self, packet):
    # TODO: Flag to route packet according to a random policy vs.
    #       according to Q-values.
    return 0

  # Generate n packets and simulate a route for all of them.
  def routePackets(self, n):
    # TODO: Generate a packet and have it routed thru
    # different nodes, adding to total travel time and
    # if dropped.
    for k in range(n):
      # TODO: Generate new packet.
      # TODO: self.routePacket(packet).
      break

    return 0

