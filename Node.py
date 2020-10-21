
# Node: ノードの情報や処理
from scipy.spatial import distance
from slime import slime
import random


class node:
  def __init__(self, number):
    self.number = number
    self.position = (0, 0)
    self.neighbor = []
    self.energy = 1
    self.buffer = 1
    self.content_store = {}
    self.pit = {}
    self.fib = {}
    self.slime = slime(self)
    self.communication_range = 60
    self.want_content = ""
    self.content_position = (0, 0)

  def move(self):
    self.position = (self.position[0] + random.uniform(-1, 1), self.position[1] + random.uniform(-1, 1))
    return

  def send_hello(self, nodes):
    self.neighbor = []
    for _node in nodes:
      if _node == self:
        continue
      if distance.euclidean(self.position, _node.position) < self.communication_range:
        self.neighbor.append(_node)
    self.slime.solve_length()
    return

  def select_next(self):
    self.slime.physarum_solver()
    self.select_node = max(self.slime.quantities, key=self.slime.quantities.get)
    return

  def send_packet(self):
    self.select_next.get_packet(self.want_content)
    print("send_packet")

  def get_packet(self, want_content):
    self.want_content = want_content
    self.send_hello()
    self.select_next()
    self.send_packet()
    print("get_pakcet")
