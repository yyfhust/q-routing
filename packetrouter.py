import abc
from random import choice
import random
import collections
import networkx as nx
import math
from enum import Enum
 
class PacketRouter(object):
  __metaclass__ = abc.ABCMeta
 
  def __init__(self, simulator):
    self.simulator = simulator
 
  @abc.abstractmethod
  def routePacketSingleStep(self, packet, node):
    pass
 
# randomly hops packet through the network
class RandomPacketRouter(PacketRouter):
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
 
  def __init__(self, simulator, penalize_drops=False, dropped_penalty=0.01, epsilon=0.05, learning_rate=0.01):
    super().__init__(simulator)
    # Q[(x, d, y)] = time that node x estimates it takes to deliver a packet P bound
    # for node d by way of x's neighbour y
    self.Q = collections.defaultdict(float)
    self.epsilon = epsilon
    self.learning_rate = learning_rate
    self.penalize_drops = penalize_drops
    self.dropped_penalty = dropped_penalty
 
  # returns True with p = epsilon
  def explore(self):
    return random.random() < self.epsilon
 
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
 
  def update_Q(self, cur, nxt, packet):
    # estimated time remaining from next node.
    _, min_q = self.min_Q(nxt, packet.dst)
    travel_time = self.simulator.traverseEdge(packet, cur, nxt)
    if self.penalize_drops and packet.dropped:
      # Penalize the Q score as a quadratic function of the number of packets
      # dropped along this edge so far.
      edge_attr = self.simulator.get_edge_attr(cur, nxt)
      _, min_q = self.min_Q(packet.src, packet.dst)
      min_q *= 1. + self.dropped_penalty * (edge_attr.dropped_packets ** (1/3))
 
    self.Q[(cur, packet.dst, nxt)] += self.learning_rate * (min_q + travel_time - self.Q[(cur, packet.dst, nxt)])
    return None if packet.dropped else nxt
 
  def routePacketSingleStep(self, packet, cur):
    if self.explore():
      nxt = choice(list(self.simulator.G.neighbors(cur)))
    else:
      nxt, _ = self.min_Q(cur, packet.dst)
 
    return self.update_Q(cur, nxt, packet)
 
# Q-router hybrid that uses RIP routing initially, then switches to Q-routing as
# Q-values become increasingly more and more accurate.
class ActionType(Enum):
  EXPLORE = 1
  RIP = 2
  QLEARN = 3
 
 
# TODO: Only works with connected graphs.
class RIPPacketRouter(PacketRouter):
  def __init__(self, simulator, epsilon=0.05, learning_rate=0.01):
    super().__init__(simulator)
 
    self.populate_routing_table()
 
  def populate_routing_table(self):
    self.routing_table = {}
 
    # Check that graph is connected.
    for src in self.simulator.G.nodes():
      for dst in self.simulator.G.nodes():
        assert(nx.has_path(self.simulator.G, src, dst))
 
    # Preprocess by finding shortest paths for all node pairings.
    for src, destinations in nx.shortest_path(self.simulator.G).items():
      for dst, path in destinations.items():
        if src == dst:
          hop = None
        else:
          hop = path[1]
        self.routing_table[(src, dst)] = hop
 
  def routePacketSingleStep(self, packet, node):
    nxt = self.routing_table[(node, packet.dst)]
    if not self.simulator.G.has_edge(node, nxt):
      nxt = choice(list(self.simulator.G.neighbors(node)))
    self.simulator.traverseEdge(packet, node, nxt)
    return None if packet.dropped else nxt
 
 
# TODO: Is it cheating if HybridRIPQPacketRouter() has access to num_nodes?
#       Seems to me a reasonable thing to provide to a router.
class HybridRIPQPacketRouter(QPacketRouter, RIPPacketRouter):
 
  def __init__(self, simulator, num_nodes, penalize_drops=False, epsilon=0.05, learning_rate=0.01, dropped_penalty=0.01, qlearn_threshold_multiplier=3000):
    super().__init__(simulator, penalize_drops=False, epsilon=0.05, learning_rate=0.01, dropped_penalty=0.01)
 
    self.elapsed = 0
    self.qlearn_threshold = qlearn_threshold_multiplier * num_nodes
 
  def explore(self):
    if self.elapsed < self.qlearn_threshold:
      return ActionType.RIP
    elif random.random() < self.epsilon:
      return ActionType.EXPLORE
    return ActionType.QLEARN
 
  def routePacketSingleStep(self, packet, cur):
    # Pick action to do next.
    action = self.explore()
    if action == ActionType.RIP:
      # Find next node with RIP routing table.
      nxt = self.routing_table[(cur, packet.dst)]
      if not self.simulator.G.has_edge(cur, nxt):
        nxt = choice(list(self.simulator.G.neighbors(cur)))
    elif action == ActionType.QLEARN:
      # Use Q Learning to find next node with min Q.
      nxt, _ = self.min_Q(cur, packet.dst)
    elif action == ActionType.EXPLORE:
      # Select a random node to explore.
      nxt = choice(list(self.simulator.G.neighbors(cur)))

    self.elapsed += 1
    return self.update_Q(cur, nxt, packet)