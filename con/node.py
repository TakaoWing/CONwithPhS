
# node: ノードの情報や処理
from con.position import position
from con.packet import data_packet
import queue
import math


class node:  # ノードの情報や処理
  que = queue.Queue()

  def __init__(self, number):
    self.is_active = True  # コンテンツが起動しているかどうか？
    self.number = number
    self.position = position(0, 0)
    self.neighbor = []
    self.energy = 1
    self.buffer = 1
    self.use_energy = 0.001
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

  def check_is_active(self):
    self.is_active = bool(self.energy > 0)
    return

  def connect_links(self, nodes):
    if not self.is_active:  # アクティブでない場合，以下の処理を行わない．
      return

    self.energy -= self.use_energy  # 通信を行うため，バッテリー残量を減少させる．

    self.neighbor = []
    for _node in nodes:
      if _node is self or not _node.is_active:  # 対象ノードが自分自身または，対象ノードが非アクティブの場合，以下の処理を行わない．
        continue
      if self.position.distance(_node.position) > self.communication_range:  # 対象ノードが通信可能距離以外の場合は，以下の処理を行わない．
        continue
      self.neighbor.append(_node)
    return

  def move(self):
    self.position.move()
    return

  def fragmentation(self):
    """
    Fragmentation: フラグメンテーション
    パケットサイズをネットワークの最大パケットサイズに収まるようにパケットを分割すること
    分割されたパケットは，自身のパケットキューに登録する．
    """
    if self.packet.content_id not in self.content_store:  # コンテンツストアに所望コンテンツのidがない場合，終了
      return
    # x Interestパケットが送信されたFaceに対して，Dataパケットを送信
    # o
    packet_num = self.content_store[self.packet.content_id].data_size / self.mtu
    ceil_packet_num = math.ceil(packet_num)
    for i in range(math.floor(packet_num)):
      data = data_packet(self, self.packet.content_id, self.mtu, max_number=ceil_packet_num, number=i)
      self.buffer_queue.put((data, self.received_node))
    if packet_num % 1:
      data = data_packet(self, self.packet.content_id, self.mtu * (packet_num % 1), max_number=ceil_packet_num, number=ceil_packet_num)
      self.buffer_queue.put((data, self.received_node))
    node.que.put(self)
    return

  def set_content(self, content):
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
    self.energy -= self.use_energy  # 通信を行うため，バッテリー残量を減少させる．
    self.neighbor = []
    for _node in nodes:
      if _node is self or not _node.is_active:
        continue
      if self.position.distance(_node.position) > self.communication_range:
        continue
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
