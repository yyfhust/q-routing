import random as rnd

# These drop rates are based off of a really rough Google
# search, so, take with a grain of salt.
MIN_DROP_RATE = 0
MAX_DROP_RATE = 0.1

# Latency rates in ms.
MIN_LATENCY = 0
MAX_LATENCY = 300
LATENCY_STD = 5

class Node:
  def __init__(self):
    self.edges = []

  def addEdge(self, edge):
    self.edges.append(edge)

class Edge:
  def __init__(self, n1, n2):
    self.n1 = n1
    self.n2 = n2

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
    return self.n1 == other.n1 and self.n2 == other.n1

class Packet:
  # Initialize path to include the source / starting node.
  def __init__(self, n1, n2):
    # Path of nodes that this packet has traversed.
    self.path = [n1]
    self.dropped = False
    self.totalTime = 0

  def getMostRecentNode(self):
    return self.path[-1]

  def addToPath(self, node):
    self.path.append(node)
