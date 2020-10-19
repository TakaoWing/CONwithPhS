
# Node: ノードの情報や処理

from slime import slime


class node:
  def __init__(self):
    self.position = (0, 0)
    self.neighbor = {}
    self.energy = 100
    self.buffer_occupancy = 0
    self.content_store = []
    self.pit = []
    self.fib = []
    self.slime = slime()

  def move(self):
    print("move!!")

  def send_hello(self):
    print("send_hello")

  def select_next(self):
    print("select_next")

  def send_packet(self):
    print("send_packet")

  def get_packet(self):
    print("get_pakcet")
