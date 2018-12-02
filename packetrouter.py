import abc
from random import choice
import random
import collections
import networkx as nx
import math

class PacketRouter:
  __metaclass__ = abc.ABCMeta

  def __init__(self, simulator):
    self.simulator = simulator

  @abc.abstractmethod
  def routePacket(self, packet):
    pass

  @abc.abstractmethod
  def routePacketSingleStep(self, packet, node):
    pass

# randomly hops packet through the network
class RandomPacketRouter(PacketRouter):
  def routePacket(self, packet):
    cur = packet.src
    while cur != packet.dst:
      nxt = self.routePacketSingleStep(packet, cur)
      if nxt is None: break
      cur = nxt

  def routePacketSingleStep(self, packet, node):
    nxt = choice(list(self.simulator.G.neighbors(node)))
    self.simulator.traverseEdge(packet, node, nxt)
    return None if packet.dropped else nxt

# performs Q-routing based on this paper (not predictive):
# https://bit.ly/2PYlvTR

# this algorithm leans heavily on using elapsed time to guide exploration
# we need to maintain some kind of clock that actually keeps track of the current time
# relative to the elapsed time from the simulation
# could be tricky, since packets are being routed in tandem
class QPacketRouter(PacketRouter):

  def __init__(self, simulator, rip_hybrid=False, penalize_drops=False, epsilon=0.05, learning_rate=0.01, dropped_penalty=0.2, elapsed_dampening=3):
    super().__init__(simulator)
    # Q[(x, d, y)] = time that node x estimates it takes to deliver a packet P bound
    # for node d by way of x's neighbour y
    self.Q = collections.defaultdict(float)
    self.epsilon = epsilon
    self.learning_rate = learning_rate
    self.penalize_drops = penalize_drops
    self.dropped_penalty = dropped_penalty
    self.rip_hybrid = rip_hybrid
    self.elapsed = 0
    self.elapsed_dampening = elapsed_dampening

    # Seed routing table if rip_hybrid.
    if self.rip_hybrid:
      self.routing_table = {}

      # Check that graph is connected.
      for src in simulator.G.nodes():
        for dst in simulator.G.nodes():
          assert(nx.has_path(simulator.G, src, dst))

      # Preprocess by finding shortest paths for all node pairings.
      for src, destinations in nx.shortest_path(simulator.G).items():
        for dst, path in destinations.items():
          if src == dst:
            hop = None
          else:
            hop = path[1]
          self.routing_table[(src, dst)] = hop

  # returns True with p = epsilon
  def explore(self):
    if self.rip_hybrid:
      return random.random() < self.epsilon
    else:
      modified_epsilon = min(1., self.epsilon * self.elapsed_dampening * math.exp(1./self.elapsed))
      return random.random() < modified_epsilon

  # returns best next step for packet from src to dst for minimized Q
  # gracefully handles dropped nodes, since it only checks Q values of neighbours currently in the graph
  def min_Q(self, src, dst):
    src_neighbours = self.simulator.G.neighbors(src)
    min_Q = float('inf')
    min_node = None
    for neighbor in src_neighbours:
      if self.Q[(src, dst, neighbor)] < min_Q:
        min_Q = self.Q[(src, dst, neighbor)]
        min_node = neighbor
    return min_node, min_Q

  def routePacket(self, packet):
    cur = packet.src
    while cur != packet.dst:
      nxt = self.routePacketSingleStep(packet, cur)
      if nxt is None: break
      cur = nxt

  def routePacketSingleStep(self, packet, node):
    self.elapsed += 1
    if self.explore():
      if self.rip_hybrid:
        nxt = self.routing_table[(node, packet.dst)]
      else:
        nxt = choice(list(self.simulator.G.neighbors(node)))
    else:
      nxt, _ = self.min_Q(node, packet.dst)

    # estimated time remaining from next node
    _, min_q = self.min_Q(nxt, packet.dst)
    travel_time = self.simulator.traverseEdge(packet, node, nxt)
    if self.penalize_drops and packet.dropped:
      # Penalize the Q score quadratically proportional to number of packets
      # dropped along this edge so far.
      edge_attr = self.simulator.get_edge_attr(node, nxt)
      _, min_q = self.min_Q(packet.src, packet.dst)
      min_q *= 1. + self.dropped_penalty * (edge_attr.dropped_packets ** (1/2))

    self.Q[(node, packet.dst, nxt)] += self.learning_rate * (min_q + travel_time - self.Q[(node, packet.dst, nxt)])
    return None if packet.dropped else nxt

# TODO: onlneighbor works with connected graphs
class RIPPacketRouter(PacketRouter):
  def __init__(self, simulator, epsilon=0.05, learning_rate=0.01):
    super().__init__(simulator)

    self.routing_table = {}

    # Check that graph is connected.
    for src in simulator.G.nodes():
      for dst in simulator.G.nodes():
        assert(nx.has_path(simulator.G, src, dst))

    # Preprocess by finding shortest paths for all node pairings.
    for src, destinations in nx.shortest_path(simulator.G).items():
      for dst, path in destinations.items():
        if src == dst:
          hop = None
        else:
          hop = path[1]
        self.routing_table[(src, dst)] = hop

  # perform dijsktras to find shortest path to compute a routing table: (x, d -> y) from node x,
  # with destination d, jump to y for the shortest path
  def routePacket(self, packet):
    cur = packet.src
    while cur != packet.dst:
      nxt = self.routePacketSingleStep(packet, cur)
      if nxt is None: break
      cur = nxt

  def routePacketSingleStep(self, packet, node):
    nxt = self.routing_table[(node, packet.dst)]
    if not self.simulator.G.has_edge(node, nxt):
      nxt = choice(list(self.simulator.G.neighbors(node)))
    self.simulator.traverseEdge(packet, node, nxt)
    return None if packet.dropped else nxt
