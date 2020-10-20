
# Node: ノードの情報や処理
from scipy.spatial import distance
from slime import slime
import random


class node:
  def __init__(self, number):
    self.number = number
    self.position = (0, 0)
    self.neighbor = []
    self.energy = 100
    self.buffer_occupancy = 0
    self.content_store = {}
    self.pit = {}
    self.fib = {}
    self.slime = slime(self)
    self.communication_range = 60
    self.want_content = ""

  def move(self):
    self.position = (self.position[0] + random.uniform(-1, 1), self.position[1] + random.uniform(-1, 1))

  def send_hello(self, nodes):
    self.neighbor = []
    for _node in nodes:
      if _node == self:
        continue
      if distance.euclidean(self.position, _node.position) < self.communication_range:
        self.neighbor.append(_node)

  def select_next(self):
    print("select_next")

  def send_packet(self):
    print("send_packet")

  def get_packet(self):
    print("get_pakcet")
