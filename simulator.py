from network import Node, Edge, Packet
from random import shuffle
import numpy as np

# These drop rates are based off of a really rough Google
# search, so, take with a grain of salt.
MIN_DROP_RATE = 0
MAX_DROP_RATE = 0.1

# Latency rates in ms.
MIN_LATENCY = 0
MAX_LATENCY = 300
LATENCY_STD = 5

class Node:
  def __init__(self, id):
    self.edges = []
    self.id = id

  def addEdge(self, edge):
    self.edges.append(edge)

class Edge:
  def __init__(self, ni_1, ni_2):
    self.ni_1 = ni_1
    self.ni_2 = ni_2

    # Generate a random latency and drop rate within a range,
    # drawn from a uniform distribution.
    self.latency = rnd.randint(MIN_LATENCY, MAX_LATENCY)
    self.dropRate = float(rnd.randint(MIN_DROP_RATE * 100, MAX_DROP_RATE  * 100)) / 100

  # Generate a travel time for a particular packet from
  # a standard Gaussian distribution.
  def getTravelTime(self):
    return rnd.gauss(self.latency, LATENCY_STD)

  def isDropped(self):
    return rnd.randint(0, 100) <= self.dropRate * 100

  def __eq__(self, other): 
    return (self.ni_1 == other.ni_2 and self.ni_2 == other.ni_1) or (self.ni_1 == other.ni_1 and self.ni_2 == other.ni_2)

  def __hash__(self):
    return hash(tuple((self.ni_1, self.ni_2)))

class Packet:
  # Initialize path to include the source / starting node.
  def __init__(self, src, dst):
    # Path of nodes that this packet has traversed.
    self.src = src
    self.dst = dst

    self.path = [src]
    self.dropped = False
    self.totalTime = 0

  def getMostRecentNode(self):
    return self.path[-1]

  def addToPath(self, node):
    self.path.append(node)

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
      node_1 = Node(i)
      ni_1 = node_1.id

      # Connect node to some n # of nodes already in self.nodes.
      # Randomly generate number of nodes to connect.
      numNodeEdges = avgEdgesPerNode
      for j in range(min(len(self.nodes), numNodeEdges)):
        ni_2 = rnd.randint(0, len(self.nodes) - 1)
        edge = Edge(ni_1, ni_2)
        
        # Avoid double edges.
        while (edge in self.edges): 
          ni_2 = rnd.randint(0, len(self.nodes) - 1)
          edge = Edge(ni_1, ni_2)

        node_1.addEdge(edge)
        self.nodes[ni_2].addEdge(edge)

      self.nodes.append(node_1)

    # Check if we have enough edges. If not, then add edges 
    # until we have enough edges.
    # TODO: Hacky and redundant code. Can conslidate.
    for i in range(numEdges - len(self.edges)):
      ni_1 = rnd.randint(0, len(self.nodes) - 1)
      ni_2 = rnd.randint(0, len(self.nodes) - 1)
      while (ni_1 == ni_2): 
        ni_2 = rnd.randint(0, len(self.nodes) - 1)

      edge = Edge(ni_1, ni_2)
      
      # Avoid double edges.
      while (edge in self.edges): 
        ni_2 = rnd.randint(0, len(self.nodes) - 1)
        edge = Edge(ni_1, ni_2)

      node_1.addEdge(edge)
      self.nodes[ni_2].addEdge(edge)
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
    ni_1 = packet.getMostRecentNode()
    ni_2 = edge.ni_2 if ni_1 == edge.ni_1 else ni_1

    packet.addToPath(ni_2)
    packet.totalTime += edge.getTravelTime()
    packet.isDropped = edge.isDropped()
    #TODO: Do something if packet is dropped, i.e. freak the fuck out

    return ni_2

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
<<<<<<< HEAD

networkSimulator = NetworkSimulator(numNodes = 40, numEdges = 400)
networkSimulator.routePackets(n = 1000)
=======
>>>>>>> a7d7b9dd5a3f9553ae567a7d43137fa38067cfa9
