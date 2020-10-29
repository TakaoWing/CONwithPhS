

class packet:
  def __init__(self, _node, content_id):
    self.living_time = 0  # 生存時間
    self.ttl = 20  # 生存可能時間
    self.content_id = content_id  # コンテンツID
    self.position_node = _node  # packeの現在地
    self.trace = []  # 辿った経路

  def is_living(self):
    print("packet::ContentID:{},TTL:{}".format(self.content_id, self.living_time))
    return self.living_time > self.ttl


class interest_packet(packet):
  def __init__(self, _node, content_id, content_positions=None):
    super().__init__(_node, content_id)
    self.content_positions = content_positions if content_positions else []  # コンテンツを保存しているノード


class data_packet(packet):
  def __init__(self, _node, content_id, data_size, user_positions=None):
    super().__init__(_node, content_id)
    self.user_positions = user_positions if user_positions else []  # ノードのpitを元に経路選択されるため，必要ではない，しかし，最適経路を選択する上では必要かも
    self.data_size = data_size  # コンテンツのデータサイズ
    self.data = 0  # パケットのデータサイズ[kbyte]
    self.max_data = 64  # 64[kbyte]
