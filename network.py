import random as rnd


# These drop rates are based off of a really rough Google
# search, so, take with a grain of salt.
MIN_DROP_RATE = 0
MAX_DROP_RATE = 0.05
DROP_MULT = 1 / MAX_DROP_RATE


# Latency rates in ms.
MIN_LATENCY = 0
MAX_LATENCY = 300
LATENCY_STD = 5
LOAD_MULTIPLIER = 0.01
LOAD_DECAY = 0.001


# Node queue processing
# Found on wikipedia that 100Mb/s network card is reasonable (might be lower for a mesh network with low-quality hardware)
# Max size of an ethernet packet is 1500 bytes
# Therefore, ~50,000 packets / s -> 50 packets/ms
# Packet processing time = 1/50 ms -> 0.02 ms
PACKET_QUEUE_TIME = 0.02


class NodeAttr:
  def __init__(self):
    self.Q = 0
    # TODO add some randomness for each node to processing time, like latency / dropRate
    self.packet_queue_time = rnd.gauss(PACKET_QUEUE_TIME, PACKET_QUEUE_TIME)

  def reset(self):
    self.Q = 0

class EdgeAttr:
  def __init__(self):
    # Generate a random latency and drop rate within a range,
    # drawn from a uniform distribution.
    self.latency = rnd.randint(MIN_LATENCY, MAX_LATENCY)
    self.dropRate = float(rnd.randint(MIN_DROP_RATE * DROP_MULT, MAX_DROP_RATE  * DROP_MULT)) / DROP_MULT
    self.dropped_packets = 0

  # Generate a travel time for a particular packet from
  # a standard Gaussian distribution.
  def getTravelTime(self):
    return float(rnd.gauss(self.latency, LATENCY_STD))

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
    self.totalTime = 0.

  def getMostRecentNode(self):
    return self.path[-1]

  def addToPath(self, node):
    self.path.append(node)

  def getSrc(self):
    return self.src

  def reset(self, totalTime=0., dropped=False):
    self.path = [self.src]
    self.dropped = dropped
    self.totalTime = totalTime

  def __str__(self):
    return " -> ".join(map(str, self.path))
