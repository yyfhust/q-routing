##
# simulator.py
# ---
# Creates a simulation of a network with randomly-generated 
# latency and packet drop rates.
##

import random as rnd
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
  def __init__(self):
    self.edges = []

  def addEdge(self, edge):
    self.edges.append(edge)

class Edge:
  def __init__(self, src, dst):
    self.src = src
    self.dst = dst

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
    return self.src == other.src and self.dst == other.src

class Packet:
  # Initialize path to include the source / starting node.
  def __init__(self, src, dst):
    # Path of nodes that this packet has traversed.
    self.path = [src]
    self.dropped = False
    self.totalTime = 0

  def addToPath(self, node):
    self.path.append(node)

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

      src = self.nodes[x]
      dst = self.nodes[y]

      edge = Edge(src, dst)
      src.addEdge(edge)
      dst.addEdge(edge)
      self.edges[i] = edge

  # TODO:
  def writeConfig(self):
    return

  # TODO:
  def readConfig(self):
    return

  # Route a single packet through a simulated route (an edge) 
  # and return the destination note.
  def routePacket(self, packet, edge):
    dst = edge.dst
    packet.addToPath(dst)
    packet.totalTime += edge.getTravelTime()
    packet.isDropped = edge.isDropped()

    print(packet)

    return dst

  # Generate n packets and simulate a route for all of them.
  def routePackets(self, n):
    # TODO: Generate a packet and have it routed thru
    # different nodes, adding to total travel time and
    # if dropped.
    return 0

networkSimulator = NetworkSimulator(numNodes = 10, numEdges = 4)
networkSimulator.routePackets(n = 1000)