
# node: ノードの情報や処理
from scipy.spatial import distance
from con.packet import interest_packet, data_packet, advertise_packet
import random
import math
import queue
import copy


class content:  # コンテンツの情報をまとめたもの
  def __init__(self, content_id, data_size):
    self.content_id = content_id  # コンテンツのid
    self.data_size = data_size  # データサイズ[byte]
    self.cash_size = 0  # キャッシュサイズ[kbyte]
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
    speed = 0.01
    self.x += random.uniform(-speed, speed)
    self.y += random.uniform(-speed, speed)

  def distance(self, other_position):
    return distance.euclidean(self.get_vector(), other_position.get_vector())


class pbrNode:  # ノードの情報や処理
  que = queue.Queue()

  def __init__(self, number):
    self.number = number
    self.position = position(0, 0)
    self.neighbor = []
    self.content_store = {}
    self.pit = {}
    self.fib = {}
    self.communication_range = 60
    self.buffer_queue = queue.Queue()
    self.packet = None
    self.select_next_node = []
    self.mtu = 1200  # MTU: Maximum Transfer Unit default 1200[byte]
    self.received_node = None
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

  def set_content(self, content_id):
    self.content_store[content_id] = content(content_id=content_id, data_size=10000)
    self.advertise_content(content_id)
    return

  def advertise_content(self, content_id):
    advertise = advertise_packet(content_id)
    self.buffer_queue((advertise, self))
    pbrNode.que.put(self)
    return

  def set_packet(self, want_content):
    self.request_content[want_content] = 0

    interest = interest_packet(want_content)

    self.buffer_queue.put((interest, self))
    pbrNode.que.put(self)
    return

  def get_packet(self, time=None):
    self.packet, self.received_node = self.buffer_queue.get()  # バッファキューからパケットと送られてきたノードを展開
    self.packet.trace.append(self.number)  # パケットの経路に自信の番号を追加

    type_packet = type(self.packet)

    if type_packet is data_packet:  # dataパケットの時
      if not self.packet.living_time:  # パケットが生成されたばかりの時
        self.pit[self.packet.content_id] = []
        self.pit[self.packet.content_id].append(self.received_node)
      else:
        if self.packet.content_id not in self.content_store:  # コンテンツストアにコンテンツIDがない時
          self.content_store[self.packet.content_id] = content(content_id="www.google.com/logo.png", data_size=10000)
        else:  # コンテンツストアにコンテンツIDがある場合
          if self.content_store[self.packet.content_id].cash_size < self.content_store[self.packet.content_id].data_size:
            self.content_store[self.packet.content_id].cash_size += self.packet.data_size
      if self.packet.content_id in self.request_content:  # パケットがコンテンツ要求端末に到達した場合
        self.packet.living_time = 255
        self.request_content[self.packet.content_id] += 1 / self.packet.max_number
        if self.request_content[self.packet.content_id] >= 1.0:
          start_time = self.get_content_time[self.packet.content_id]
          self.get_content_time[self.packet.content_id] = (time - start_time) * 20
        # print("コンテンツ{}到着！経路{}".format(self.packet.number, self.packet.trace))

    if self.packet.is_living():
      self.packet = None

    return

  def check_have_content(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    if not self.content_store:  # コンテンツストアが空の場合，終了
      return
    if self.packet.content_id not in self.content_store:  # コンテンツストアにコンテンツIDを持ったコンテンツがない場合以下の処理を実行しない
      return
    self.fragmentation()  # フラグメンテーションを実行
    self.packet = None  # パケットを破棄する
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
    pbrNode.que.put(self)
    return

  def check_have_pit(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
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
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    self.select_next_node = []
    return

  def select_next_data(self):
    if self.packet is None:
      return
    if self.packet.content_id not in self.pit:  # PITにContentIDが含まれている場合
      self.packet = None
      return
    self.select_next_node = []
    self.select_next_node.extend(self.pit[self.packet.content_id])  # Dataパケットを送信するノードにPITのContentIDに紐づいているFaceをすべて登録する
    return

  def write_pit(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return

    if self.packet.content_id in self.pit:  # 自身のPITにpacketのコンテンツIDが含まれているかどうか
      # PITのコンテンツIDの中に前のノードがない場合，追加する
      if self.received_node not in self.pit[self.packet.content_id]:
        self.pit[self.packet.content_id].append(self.received_node)
    else:  # PITにない場合，新しく登録する
      self.pit[self.packet.content_id] = []
      self.pit[self.packet.content_id].append(self.received_node)

    for k, v in self.pit.items():
      for n in v:
        print("table_name:self.pit,Content_id:{},Node:{}".format(k, n.number))
    return

  def send_packet(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return

    flag_send_data_packet = False
    if type(self.packet) is data_packet:  # パケットがdataパケットの時
      if not self.packet.living_time:
        flag_send_data_packet = self.packet.max_number is not self.packet.number

    self.packet.living_time += 1
    for sn in self.select_next_node:
      sn.buffer_queue.put((copy.deepcopy(self.packet), self))
      pbrNode.que.put(sn)
    if flag_send_data_packet:
      pbrNode.que.put(self)
    self.packet_type = str(type(self.packet))
    self.packet = None
    return

  def interest_packet_protocol(self, nodes):
    # content_storeにコンテンツがあるか確認 -(yes)> pitを元にdataパケットを送信する -> Interestパケットを破棄する
    self.check_have_content()
    # pitに要求されたコンテンツ名があるか確認 -(yes)> pitにInterestパケットを受信したフェイスを追記する -> Interestパケットを廃棄する
    self.check_have_pit()
    # fibに要求されたコンテンツ名があるか確認 -(no,yes)> フィザルムソルバーによって，fibを変更する
    self.check_have_fib()
    # pitにinterestパケットを受信したフェイスを記入する
    self.write_pit()
    return

  def data_packet_protocol(self, nodes):
    # 接続状態を確認
    self.send_hello(nodes)
    # 次のノードを選択
    self.select_next_data()
    return

  def advertise_packet_protocol(self, nodes):
    # Potentialの計算
    self.put_potential()

    # 接続状況を確認
    self.send_hello(nodes)
    # 次のノードを選択

    return

  def packet_protocol(self, nodes, time=None):
    # パケットの受信
    self.get_packet(time=time)

    if self.packet is None:  # パケットが破棄されている場合
      return  # プロトコルを終了する

    type_packet = type(self.packet)

    # 受信したパケットの種類によって，プロトコルを変更する
    if type_packet is interest_packet:  # interestパケットの時
      self.interest_packet_protocol(nodes)
    elif type_packet is data_packet:  # dataパケットの時
      self.data_packet_protocol(nodes)
    elif type_packet is advertise_packet:  # advertiseパケットの時
      self.advertise_packet_protocol(nodes)

    # パケットを転送する
    self.send_packet()
    return
