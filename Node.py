
# node: ノードの情報や処理
from scipy.spatial import distance
from slime import slime
from packet import interest_packet
from packet import data_packet
import random
import math
import queue


class content:  # コンテンツの情報をまとめたもの
  def __init__(self, content_id, data_size):
    self.content_id = content_id  # コンテンツのid
    self.data_size = data_size  # データサイズ[kbyte]
    self.case_size = 0  # キャッシュサイズ[kbyte]
    self.ttl = 255  # コンテンツの公開時間[s]
    self.packets = math.ceil(self.data_size / 64)  # コンテンツのパケット数


class position:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.vector = (self.x, self.y)

  def set_vector(self, x, y):
    self.x = x
    self.y = y
    self.vector = (self.x, self.y)

  def get_vector(self):
    self.vector = (self.x, self.y)
    return self.vector

  def move(self):
    self.x += random.uniform(-1, 1)
    self.y += random.uniform(-1, 1)

  def distance(self, other_position):
    return distance.euclidean(self.get_vector(), other_position.get_vector())


class node:  # ノードの情報や処理
  que = queue.Queue()

  def __init__(self, number):
    self.number = number
    self.position = position(0, 0)
    self.neighbor = []
    self.energy = 1
    self.buffer = 1
    self.content_store = []
    self.pit = {}
    self.fib = {}
    self.slime = slime(self)
    self.communication_range = 60
    self.content_position = position(0, 0)
    self.buffer_queue = queue.Queue()
    self.packet = None

  def move(self):
    self.position.move()
    return

  def send_hello(self, nodes):
    if type(self.packet) is data_packet:  # パケットの種類がdata packetなら以下の処理を実行しない
      return
    self.neighbor = []
    for _node in nodes:
      if _node == self:
        continue
      if self.position.distance(_node.position) < self.communication_range:
        self.neighbor.append(_node)
    self.slime.solve_length()
    return

  def select_next(self):
    if type(self.packet) is data_packet:  # パケットの種類がdata packetなら以下の処理を実行しない
      self.select_next = self.pit[self.packet.content_id]
    else:
      self.slime.physarum_solver()
      self.select_node = max(self.slime.quantities, key=self.slime.quantities.get)
    return

  def write_pit(self):
    if type(self.packet) is data_packet:  # パケットの種類がdata packetなら以下の処理を実行しない
      return
    return

  def send_packet(self):
    if type(self.packet) is data_packet:  # パケットの種類がdata packetなら以下の処理を実行しない
      return
    self.select_next.buffer_queue.put(self.packet)
    self.packet = None
    node.que.set(self.select_next)
    return

  def check_have_content(self, content):
    if not self.content_store:  # コンテンツストアが空の場合，終了
      return
    content_ids = [file.content_id for file in self.content_store]
    if content.content_id not in content_ids:  # コンテンツストアに所望コンテンツのidがない場合，終了
      return
    content_store_index = content_ids.index(content.content_id)
    self.packet = data_packet(self, content.id)
    self.packet.data_size = self.content_store[content_store_index].data_size
    return

  def check_have_pit(self, content):
    if type(self.packet) is data_packet:  # パケットの種類がdata packetなら以下の処理を実行しない
      return
    return

  def set_packet(self, want_content):
    self.buffer_queue.put(interest_packet(self, want_content))
    node.que.put(self)
    return

  def get_packet(self, want_content):
    # content_storeにコンテンツがあるか確認 -(yes)> pitを元にdataパケットを送信する -> Interestパケットを破棄する
    self.check_have_content()
    # pitに要求されたコンテンツ名があるか確認 -(yes)> pitにInterestパケットを受信したフェイスを追記する -> Interestパケットを廃棄する
    self.check_have_pit()
    # fibに要求されたコンテンツ名があるか確認 -(no,yes)> フィザルムソルバーによって，fibを変更する
    # self.check_have_fib()
    # 接続状態を確認
    self.send_hello()
    # 次のノードを選択
    self.select_next()
    # pitにinterestパケットを受信したフェイスを記入する
    self.write_pit()
    # パケットを転送する
    self.send_packet()
    return
