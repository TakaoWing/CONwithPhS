
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
    self.slimes = {}
    self.communication_range = 60
    self.content_position = position(0, 0)
    self.buffer_queue = queue.Queue()
    self.packet = None
    self.select_next_node = []

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
    self.buffer_queue.put(interest_packet(self, want_content, content_positions))
    node.que.put(self)
    return

  def get_packet(self):
    # if self.packet is not None:  # パケットを持っているなら処理を実行しない．　
    #   return
    self.packet = self.buffer_queue.get()
    if self.packet.is_living():  # パケットがTTL以上の場合破棄する
      self.packet = None
    return

  def check_have_content(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    if not self.content_store:  # コンテンツストアが空の場合，終了
      return
    content_ids = [file.content_id for file in self.content_store]
    if self.packet.content_id not in content_ids:  # コンテンツストアに所望コンテンツのidがない場合，終了
      return
    # Interestパケットが送信されたFaceに対して，Dataパケットを送信
    content_store_index = content_ids.index(self.packet.content_id)
    self.packet.position_node.buffer_queue.put(data_packet(self, self.packet.content_id, self.content_store[content_store_index].data_size))
    node.que.put(self.packet.position_node)
    self.packet = None  # パケットを破棄する
    return

  def check_have_pit(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    if self.packet.content_id not in self.pit:  # 自身のPITにpacketのコンテンツIDが含まれているかどうか
      return
    if self.packet.position_node in self.pit[self.packet.content_id]:  # PITのコンテンツIDの中に前のノードがない場合，追加する
      return
    self.pit[self.packet.content_id].append(self.packet.position_node)
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
    if type(self.packet) is data_packet:  # パケットの種類がdata packetなら以下の処理を実行しない
      return
    # self.slime.init_physarum_solver()
    return

  # def select_next(self):
  #   if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
  #     return
  #   self.select_next_node = []
  #   if type(self.packet) is data_packet:  # パケットの種類がdata packetなら以下の処理を実行しない
  #     if self.packet.content_id in self.pit:  # PITにContentIDが含まれている場合
  #       self.select_next_node.extend(list(face for face in self.pit[self.packet.content_id]))  # Dataパケットを送信するノードにPITのCOntentIDに紐づいているFaceをすべて登録する
  #     else:
  #       # if self.packet.position_node not in self.select_next_node:  # PITにInterestパケットが送信されたノードが含まれてない場合
  #       self.select_next_node.append(self.packet.position_node)  # 次に送信するノードに登録する
  #   else:
  #     if self.packet.content_id in self.slimes:
  #       self.slimes[self.packet.content_id].physarum_solver()
  #     else:
  #       self.slimes[self.packet.content_id] = slime(self)
  #       self.slimes[self.packet.content_id].init_physarum_solver()
  #     for (k, v) in self.slimes[self.packet.content_id].quantities.items():
  #       print("{}:{}".format(k.number, v))

  #     self.select_next_node.append(max(self.slimes[self.packet.content_id].quantities, key=self.slimes[self.packet.content_id].quantities.get))
  #   return

  def select_next(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    self.select_next_node = []
    if self.packet.content_id in self.slimes:
      self.slimes[self.packet.content_id].physarum_solver()
    else:
      self.slimes[self.packet.content_id] = slime(self)
      self.slimes[self.packet.content_id].init_physarum_solver()
    for (k, v) in self.slimes[self.packet.content_id].quantities.items():
      print("{}:{}".format(k.number, v))

    self.select_next_node.append(max(self.slimes[self.packet.content_id].quantities, key=self.slimes[self.packet.content_id].quantities.get))
    return

  def select_next_data(self):
    if self.packet is None:
      return
    if self.packet.content_id not in self.pit:  # PITにContentIDが含まれている場合
      self.packet = None
      return
    self.select_next = []
    self.select_next_node.extend(list(face for face in self.pit[self.packet.content_id]))  # Dataパケットを送信するノードにPITのCOntentIDに紐づいているFaceをすべて登録する
    return

  def write_pit(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    if self.packet.content_id in self.pit:  # 自身のPITにpacketのコンテンツIDが含まれているかどうか
      # PITのコンテンツIDの中に前のノードがない場合，追加する
      if self.packet.position_node not in self.pit[self.packet.content_id]:
        self.pit[self.packet.content_id].append(self.packet.position_node)
    else:  # PITにない場合，新しく登録する
      self.pit[self.packet.content_id] = []
      self.pit[self.packet.content_id].append(self.packet.position_node)
    return

  def send_packet(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    if type(self.packet) is interest_packet:  # パケットの種類がdata packetなら以下の処理を実行しない
      self.packet.position_node = self

    self.packet.living_time += 1
    for sn in self.select_next_node:
      sn.buffer_queue.put(self.packet)
      node.que.put(sn)
    if type(self.packet) is data_packet:
      self.buffer_queue.put(self.packet)
      node.que.put(self)
    self.packet = None
    return

  def interest_packet_protocol(self, nodes):
    # content_storeにコンテンツがあるか確認 -(yes)> pitを元にdataパケットを送信する -> Interestパケットを破棄する
    self.check_have_content()
    # pitに要求されたコンテンツ名があるか確認 -(yes)> pitにInterestパケットを受信したフェイスを追記する -> Interestパケットを廃棄する
    self.check_have_pit()
    # fibに要求されたコンテンツ名があるか確認 -(no,yes)> フィザルムソルバーによって，fibを変更する
    # self.check_have_fib()
    # 接続状態を確認
    self.send_hello(nodes)
    # 次のノードを選択
    self.select_next()
    # pitにinterestパケットを受信したフェイスを記入する
    self.write_pit()
    return

  def data_packet_protocol(self, nodes):
    # 接続状態を確認
    self.send_hello(nodes)
    # 次のノードを選択
    self.select_next_data()
    return

  def packet_protocol(self, nodes):
    # パケットの受信
    self.get_packet()

    # 受信したパケットの種類によって，プロトコルを変更する
    if type(self.packet) is interest_packet:
      self.interest_packet_protocol(nodes)
    else:
      self.data_packet_protocol(nodes)

    # パケットを転送する
    self.send_packet()
    return
