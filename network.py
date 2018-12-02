import random as rnd

# These drop rates are based off of a really rough Google
# search, so, take with a grain of salt.
MIN_DROP_RATE = 0
MAX_DROP_RATE = 0.005
DROP_MULT = 1 / MAX_DROP_RATE

# Latency rates in ms.
MIN_LATENCY = 0
MAX_LATENCY = 300
LATENCY_STD = 5
LOAD_MULTIPLIER = 0.01
LOAD_DECAY = 0.01

class NodeAttr:
  def __init__(self):
    self.Q = 0

  def reset(self):
    self.Q = 0

class EdgeAttr:
  def __init__(self):
    # Generate a random latency and drop rate within a range,
    # drawn from a uniform distribution.
    self.latency = rnd.randint(MIN_LATENCY, MAX_LATENCY)
    self.dropRate = float(rnd.randint(MIN_DROP_RATE * DROP_MULT, MAX_DROP_RATE  * DROP_MULT)) / DROP_MULT
    self.load = 0
    self.dropped_packets = 0

  def increase_load(self):
    self.load += 1

  def decrease_load(self):
    self.load = self.load * LOAD_DECAY

  # Generate a travel time for a particular packet from
  # a standard Gaussian distribution.
  def getTravelTime(self):
    return rnd.gauss(self.latency, LATENCY_STD) * (1 + LOAD_MULTIPLIER * self.load)

  def isDropped(self):
    isDropped = rnd.randint(0, DROP_MULT) < self.dropRate * DROP_MULT
    # TODO: Maybe this isn't the best place for dropped_packets += 1 logic.
    if isDropped: self.dropped_packets += 1
    return isDropped

  def reset(self):
    self.load = 0
    self.dropped_packets = 0

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

  def resetPath(self):
    self.path = [self.src]
    self.dropped = False

  def getSrc(self):
    return self.src

  def reset(self):
    self.path = [self.src]
    self.dropped = False
    self.dropped_packets = 0
    self.totalTime = 0

  def __str__(self):
    return " -> ".join(map(str, self.path))
