
# node: ノードの情報や処理
from con.content import content
from con.position import position
from con.slime import slime
from con.packet import interest_packet, data_packet, slime_interest_packet, slime_data_packet
import math
import queue
import copy


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
    self.f_pit = {}
    self.fib = {}
    self.slimes = {}
    self.communication_range = 60
    self.content_position = position(0, 0)
    self.buffer_queue = queue.Queue()
    self.packet = None
    self.select_next_node = []
    self.mtu = 1200  # MTU: Maximum Transfer Unit default 1200[byte]
    self.received_node = None
    self.request_content = {}  # request_content: {content_id,data_size}
    self.get_content_time = {}
    self.packet_type = ""
    self.flatting_request_packet = []

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
    self.request_content[want_content] = 0

    if content_positions:  # コンテンツ情報があるかどうかで生成するパケットの種類を変更
      interest = interest_packet(want_content, content_positions)
    else:
      interest = slime_interest_packet(want_content)

    self.buffer_queue.put((interest, self))
    node.que.put(self)
    return

  def get_packet(self, time=None):
    self.packet, self.received_node = self.buffer_queue.get()  # バッファキューからパケットと送られてきたノードを展開
    self.packet.trace.append(self.number)  # パケットの経路に自信の番号を追加

    type_packet = type(self.packet)

    if type_packet is interest_packet:  # interestパケットの時
      if self.packet.randam_bin in list(_packet.randam_bin for _packet in self.flatting_request_packet):
        self.packet.living_time = 255
    elif type_packet is data_packet:  # dataパケットの時
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
    elif type_packet is slime_interest_packet:  # slime-interestパケットの時
      if not self.packet.living_time:
        self.get_content_time[self.packet.content_id] = time
      if self.packet.randam_bin in list(_packet.randam_bin for _packet in self.flatting_request_packet):
        self.packet.living_time = 255
    elif type_packet is slime_data_packet:  # slime-dataパケットの時
      if not self.packet.living_time:  # パケットが生成されたばかりの時
        fpit_index = self.packet.get_fpit_index()
        self.f_pit[fpit_index] = []
        self.f_pit[fpit_index].append(self.received_node)
      if self.packet.content_id in self.request_content:  # パケットがコンテンツ要求端末に到達した場合
        self.packet.living_time = 255
        print("リクエス到着！経路{}".format(self.packet.trace))
        if self.packet.content_id not in self.content_store:  # コンテンツストアにコンテンツがない場合
          self.set_packet(self.packet.content_id, self.packet.content_position)  # Interest Packetを送信

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

  def check_have_content_slime(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    if not self.content_store:  # コンテンツストアが空の場合，終了
      return
    if self.packet.content_id not in self.content_store:  # コンテンツストアにコンテンツIDを持ったコンテンツがない場合以下の処理を実行しない
      return

    self.flatting_request_packet.append(self.packet)
    request = slime_data_packet(self.packet.content_id, self.position, self.packet.randam_bin)
    self.buffer_queue.put((request, self.received_node))
    node.que.put(self)

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
    node.que.put(self)
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
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    self.select_next_node = []

    if self.packet.content_id not in self.slimes:
      self.slimes[self.packet.content_id] = slime(self)

    self.slimes[self.packet.content_id].physarum_solver()

    for (k, v) in self.slimes[self.packet.content_id].tubes.items():
      print("Node {}:{}".format(k.number, vars(v)))

    quantities = self.slimes[self.packet.content_id].get_quantities()
    self.select_next_node.append(max(quantities, key=quantities.get))
    return

  def select_next_slime(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    self.select_next_node = []
    self.select_next_node.extend(self.neighbor)  # 隣接ノードにInterestパケットを送信する
    if self.received_node in self.select_next_node:  # 送られてきたノードが次に送るリストにある場合
      self.select_next_node.remove(self.received_node)  # 送られてきたノードに対して，パケットを送信しない
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

  def select_next_slime_data(self):
    if self.packet is None:
      return
    fpit_index = self.packet.get_fpit_index()
    if fpit_index not in self.f_pit:  # PITにContentIDが含まれている場合
      self.packet = None
      return
    self.select_next_node = []
    self.select_next_node.extend(list(face for face in self.f_pit[fpit_index]))  # Dataパケットを送信するノードにPITのContentIDに紐づいているFaceをすべて登録する
    del self.f_pit[fpit_index]
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

  def write_pit_slime(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return

    fpit_index = self.packet.get_fpit_index()
    if fpit_index in self.f_pit:  # 自身のPITにpacketのコンテンツIDが含まれているかどうか
      # PITのコンテンツIDの中に前のノードがない場合，追加する
      if self.received_node not in self.f_pit[fpit_index]:
        self.f_pit[fpit_index].append(self.received_node)
    else:  # PITにない場合，新しく登録する
      self.f_pit[fpit_index] = []
      self.f_pit[fpit_index].append(self.received_node)

    for k, v in self.f_pit.items():
      for n in v:
        print("table_name:f_pit,Content_id:{},Node:{}".format(k, n.number))
    return

  def send_packet(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return

    flag_send_data_packet = False
    if type(self.packet) is data_packet:  # パケットがdataパケットの時
      if not self.packet.living_time:
        flag_send_data_packet = self.packet.max_number is not self.packet.number
    elif type(self.packet) is slime_interest_packet:  # パケットがinterestパケットの時
      self.flatting_request_packet.append(self.packet)

    self.packet.living_time += 1
    for sn in self.select_next_node:
      sn.buffer_queue.put((copy.deepcopy(self.packet), self))
      node.que.put(sn)
    if flag_send_data_packet:
      node.que.put(self)
    self.packet_type = str(type(self.packet))
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

  def slime_interest_packet_protocol(self, nodes):
    # content_storeにコンテンツがあるか確認 -(yes)> pitを元にdataパケットを送信する -> Interestパケットを破棄する
    self.check_have_content_slime()
    # 接続状態を確認
    self.send_hello(nodes)
    # 次のノードを選択
    self.select_next_slime()
    # pitにinterestパケットを受信したフェイスを記入する
    self.write_pit_slime()
    return

  def slime_data_packet_protocol(self, nodes):
    # 接続状態を確認
    self.send_hello(nodes)
    # 次のノードを選択
    self.select_next_slime_data()
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
    elif type_packet is slime_interest_packet:  # slime-interestパケットの時
      self.slime_interest_packet_protocol(nodes)
    elif type_packet is slime_data_packet:  # slime-dataパケットの時
      self.slime_data_packet_protocol(nodes)

    # パケットを転送する
    self.send_packet()
    return
