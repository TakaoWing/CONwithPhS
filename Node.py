
# Node: ノードの情報や処理
from scipy.spatial import distance
from slime import slime


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
    self.slime = slime()

  def move(self):
    print("move!!")

  def send_hello(self, nodes):
    for _node in nodes:
      if _node == self:
        continue
      if distance.euclidean(self.position, _node.position) < 1.5:
        self.neighbor.append(_node)

  def select_next(self):
    print("select_next")

  def send_packet(self):
    print("send_packet")

  def get_packet(self):
    print("get_pakcet")
