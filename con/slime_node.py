
# node: ノードの情報や処理
from con.node import node
from con.content import content
from con.position import position
from con.slime import slime
from con.packet import interest_packet, data_packet, slime_interest_packet, slime_data_packet
import copy


class slime_node(node):  # ノードの情報や処理

  def __init__(self, number):
    super().__init__(number)
    self.f_pit = {}
    self.slimes = {}
    self.content_position = position(0, 0)
    self.received_node = None
    self.flatting_request_packet = []
    self.want_content_num = 1

  def connect_links(self, nodes):
    if not self.is_active:  # アクティブでない場合，以下の処理を行わない．
      return

    self.energy -= self.use_energy / 1000  # 通信を行うため，バッテリー残量を減少させる．

    self.neighbor = []

    for _node in nodes:
      if _node is self or not _node.is_active:  # 自分自身または，処理対象ノードがアクティブでなければ以下の処理を行わない．
        continue
      if self.position.distance(_node.position) > self.communication_range:  # 通信可能距離以内でなければ，以下の処理を行わない．
        continue
      self.neighbor.append(_node)
      if not _node.content_store:  # コンテンツストアが空の場合，以下の処理を行わない．
        continue
      for content_id in _node.content_store.keys():
        if not self.slimes or content_id not in self.slimes:  # 自身のスライムが存在しないまたは，自身のスライムが存在していてもcontent_idが存在しない場合，
          self.slimes[content_id] = slime(self, _node.position)
        else:
          self.slimes[content_id].content_position = _node.position
    return

  def set_content(self, content):
    self.content_store[content.content_id] = content
    return

  def set_packet(self, want_content, content_positions=None):
    self.request_content[want_content] = 0

    if content_positions:  # コンテンツ情報があるかどうかで生成するパケットの種類を変更
      interest = interest_packet(want_content, content_positions)
    else:
      interest = slime_interest_packet(want_content)

    self.buffer_queue.put((interest, self))
    # node.que.put(self)
    return

  def get_packet(self, time=None):
    if not self.is_active:  # アクティブでない場合，以下の処理を行わない．
      return
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
          self.content_store[self.packet.content_id] = content(content_id=self.packet.content_id, data_size=3600)  # def:data_size = 10000
          self.content_store[self.packet.content_id].cash_size += self.packet.data_size
          self.packet.living_time = 255
        else:  # コンテンツストアにコンテンツIDがある場合
          self.content_store[self.packet.content_id].cash_size += self.packet.data_size
          if self.content_store[self.packet.content_id].cash_size < self.content_store[self.packet.content_id].data_size:
            self.packet.living_time = 255
          else:
            if self.packet.content_id not in self.request_content:
              self.fragmentation(send_nodes=self.pit[self.packet.content_id])
            self.packet.living_time = 255
      if self.packet.content_id in self.request_content:  # パケットがコンテンツ要求端末に到達した場合
        self.packet.living_time = 255
        self.request_content[self.packet.content_id] += 1 / self.packet.max_number
        if self.request_content[self.packet.content_id] >= 1.0:
          start_time = self.get_content_time[self.packet.content_id]
          self.get_content_time[self.packet.content_id] = (time - start_time) * 20
          del self.request_content_times[self.packet.content_id]  # 再送は行わないため，削除する
          del self.backup_interest_packets_positions[self.packet.content_id]  # 再送は行わないため，削除する
          self.set_packet("www.google.com/logo{}.png".format(self.want_content_num))
          self.want_content_num += 1
          self.is_check_battery = True
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
          self.request_content_times[self.packet.content_id] = 0
          self.backup_interest_packets_positions[self.packet.content_id] = self.packet.content_position

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
    # node.que.put(self)

    self.packet = None  # パケットを破棄する
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

  def select_next(self):
    if self.packet is None:  # パケットが破棄されている場合以下の処理を行わない
      return
    self.select_next_node = []

    if self.packet.content_id not in self.slimes:
      self.slimes[self.packet.content_id] = slime(self, self.packet.content_positions)
    else:
      self.slimes[self.packet.content_id].content_position = self.packet.content_positions

    self.slimes[self.packet.content_id].physarum_solver()

    for (k, v) in self.slimes[self.packet.content_id].tubes.items():
      print("Node {}:{}".format(k.number, vars(v)))

    quantities = self.slimes[self.packet.content_id].get_quantities()
    if self.received_node in quantities:
      del quantities[self.received_node]
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

    self.energy -= self.use_energy  # 通信を行うため，バッテリー残量を減少させる．

    # flag_send_data_packet = False
    # if type(self.packet) is data_packet:  # パケットがdataパケットの時
    #   if not self.packet.living_time:
    #     flag_send_data_packet = self.packet.max_number is not self.packet.number
    # elif
    if type(self.packet) is slime_interest_packet:  # パケットがinterestパケットの時
      self.flatting_request_packet.append(self.packet)

    self.packet.living_time += 1
    for sn in self.select_next_node:
      if sn not in self.neighbor:
        continue
      sn.buffer_queue.put((copy.deepcopy(self.packet), self))
      # node.que.put(sn)
    # if flag_send_data_packet:
      # node.que.put(self)
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

  def update_physarum(self):
    if not self.slimes:
      return
    for _slime in self.slimes.values():
      _slime.physarum_solver()
      for (k, v) in _slime.tubes.items():
        print("Node{}→Node{} :{}".format(self.number, k.number, vars(v)))
    return

  def update_repuest_content_times(self):
    for content_id in self.request_content_times.keys():  # 要求コンテンツ数カウントを増やす
      self.request_content_times[content_id] += 1
      if self.request_content_times[content_id] >= 100:  # 指定時間を超えている場合，再送する
        self.set_packet(content_id, self.backup_interest_packets_positions[content_id])  # Interest Packetを送信
        self.request_content_times[content_id] = 0  # 再送を行なったため，時間をリセットする
    return
