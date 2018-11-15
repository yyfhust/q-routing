from network import Node, Edge, Packet
from random import shuffle
import numpy as np

class NetworkSimulator:
  # numNodes : # of nodes in the randomly gen. network
  # numEdges : # of edges in the randomly gen. network
  def __init__(self, numNodes, numEdges):
    self.numNodes = numNodes
    self.numEdges = numEdges
    self.packets = []

    self.nodes = [Node() for x in range(numNodes)]

    # Randomly generate all possible edges then shuffle and truncate.
    self.edges = [(x, y) for x in range(numNodes) for y in range(numNodes) if x != y]
    shuffle(self.edges)
    self.edges = self.edges[:numEdges]

    for i in range(numEdges):
      x, y = self.edges[i]

      n1 = self.nodes[x]
      n2 = self.nodes[y]

      edge = Edge(n1, n2)
      n1.addEdge(edge)
      n2.addEdge(edge)
      self.edges[i] = edge

  # TODO: Save network node and edge configurations into a file.
  def writeConfig(self):
    return

  # TODO: Load network node and edge configurations from a file.
  def readConfig(self):
    return

  # Route a single packet through a simulated route (an edge)
  # and return the destination note.
  def routePacket(self, packet, edge):
    # Get most recently traveled node and find the other
    # node in the edge.
    n1 = packet.getMostRecentNode()
    # TODO: assert that there exists an edge leading away from n1
    n2 = edge.n2 if n1 == edge.n1 else n1

    packet.addToPath(n2)
    packet.totalTime += edge.getTravelTime()
    packet.isDropped = edge.isDropped()
    #TODO: Do something if packet is dropped, i.e. freak the fuck out

    return n2

  # Generate n packets and simulate a route for all of them.
  def routePackets(self, n):
    # TODO: Generate a packet and have it routed thru
    # different nodes, adding to total travel time and
    # if dropped.
    return 0
