
# node: ノードの情報や処理
from con.position import position
import queue


class node:  # ノードの情報や処理
  que = queue.Queue()

  def __init__(self, number):
    self.number = number
    self.position = position(0, 0)
    self.neighbor = []
    self.energy = 1
    self.buffer = 1
    self.content_store = {}
    self.pit = {}
    self.fib = {}
    self.communication_range = 60
    self.buffer_queue = queue.Queue()
    self.packet = None
    self.select_next_node = []
    self.mtu = 1200  # MTU: Maximum Transfer Unit default 1200[byte]
    self.request_content = {}  # request_content: {content_id,data_size}
    self.get_content_time = {}
    self.packet_type = ""

  def connect_links(self, nodes):
    self.neighbor = []
    for _node in nodes:
      if _node is self:
        continue
      if self.position.distance(_node.position) < self.communication_range:
        self.neighbor.append(_node)
    return

  def move(self):
    self.position.move()
    return

  def set_packet(self, want_content, content_positions=None):
    return

  def get_packet(self, time=None):
    return

  def check_have_content(self):
    return

  def check_have_pit(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    if not self.packet.content_positions:  # コンテンツ保持端末の場所を知らない場合
      return
    if self.packet.content_id not in self.pit:  # 自身のPITにpacketのコンテンツIDが含まれているかどうか
      return
    if self.received_node in self.pit[self.packet.content_id]:  # PITのコンテンツIDの中に前のノードがない場合，追加する
      return
    self.pit[self.packet.content_id].append(self.received_node)
    self.packet = None  # Interestパケットを廃棄する
    return

  def send_hello(self, nodes):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    self.neighbor = []
    for _node in nodes:
      if _node is self:
        continue
      if self.position.distance(_node.position) < self.communication_range:
        self.neighbor.append(_node)
    return

  def select_next(self):
    return

  def write_pit(self):
    return

  def send_packet(self):
    return

  def interest_packet_protocol(self, nodes):
    return

  def data_packet_protocol(self, nodes):
    return

  def packet_protocol(self, nodes, time=None):
    return
