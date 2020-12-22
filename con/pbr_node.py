
# node: ノードの情報や処理
from con.node import node
from con.packet import interest_packet, data_packet, advertise_packet
from con.content import content
import copy


class pbr_node(node):  # ノードの情報や処理

  def __init__(self, number):
    super().__init__(number)
    self.potentials = {}  # potentials : {content_id, potential_value}

  def set_content(self, content):
    self.content_store[content.content_id] = content
    self.advertise_content(content.content_id)
    return

  def advertise_content(self, content_id):
    advertise = advertise_packet(content_id, self.position)
    self.buffer_queue.put((advertise, self))
    self.que.put(self)
    return

  def set_packet(self, want_content):
    self.request_content[want_content] = 0

    interest = interest_packet(want_content)

    self.buffer_queue.put((interest, self))
    self.que.put(self)
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
          # start_time = self.get_content_time[self.packet.content_id]
          self.get_content_time[self.packet.content_id] = (time) * 20
        # print("コンテンツ{}到着！経路{}".format(self.packet.number, self.packet.trace))
    elif type_packet is advertise_packet:
      if self.packet.content_id in self.potentials:
        self.packet.living_time = 255

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

  def check_have_pit(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    if self.packet.content_id not in self.pit:  # 自身のPITにpacketのコンテンツIDが含まれているかどうか
      self.set_packet(self.packet.content_positions)
      self.packet = None  # Interestパケットを廃棄する
      return
    if self.received_node in self.pit[self.packet.content_id]:  # PITのコンテンツIDの中に前のノードがない場合，追加する
      return
    self.pit[self.packet.content_id].append(self.received_node)
    self.packet = None  # Interestパケットを廃棄する
    return

  def select_next(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    self.select_next_node = []
    potential_values = {}
    for _neighbor in self.neighbor:
      potential_values[_neighbor] = _neighbor.potentials[self.packet.content_id]

    self.select_next_node.append(min(potential_values, key=potential_values.get))
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

  def selct_next_advertise(self):
    if self.packet is None:
      return
    self.select_next_node = []
    self.select_next_node.extend(self.neighbor)
    if self.received_node in self.select_next_node:
      self.select_next_node.remove(self.received_node)
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

    self.energy -= self.use_energy  # 通信を行うため，バッテリー残量を減少させる．

    flag_send_data_packet = False
    if type(self.packet) is data_packet:  # パケットがdataパケットの時
      if not self.packet.living_time:
        flag_send_data_packet = self.packet.max_number is not self.packet.number

    self.packet.living_time += 1
    for sn in self.select_next_node:
      sn.buffer_queue.put((copy.deepcopy(self.packet), self))
      self.que.put(sn)
    if flag_send_data_packet:
      self.que.put(self)
    self.packet_type = str(type(self.packet))
    self.packet = None
    return

  def put_potential(self):
    self.potentials[self.packet.content_id] = - self.packet.quality_content / (self.position.distance(self.packet.content_position) + 1e-25) ** self.packet.living_time
    return

  def interest_packet_protocol(self, nodes):
    # content_storeにコンテンツがあるか確認 -(yes)> pitを元にdataパケットを送信する -> Interestパケットを破棄する
    self.check_have_content()
    # pitに要求されたコンテンツ名があるか確認 -(yes)> pitにInterestパケットを受信したフェイスを追記する -> Interestパケットを廃棄する
    self.check_have_pit()
    # fibに要求されたコンテンツ名があるか確認 -(no,yes)> フィザルムソルバーによって，fibを変更する
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

  def advertise_packet_protocol(self, nodes):
    # Potentialの計算
    self.put_potential()
    # 接続状況を確認
    self.send_hello(nodes)
    # 次のノードを選択
    self.selct_next_advertise()
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
