

class packet:
  def __init__(self, _node, content_id):
    self.living_time = 0  # 生存時間
    self.TTL = 20  # 生存可能時間
    self.content_id = content_id  # コンテンツID
    self.position_node = _node  # packetの現在地
    self.trace = []  # 辿った経路


class interest_packet(packet):
  def __init__(self, _node, content_id):
    super(packet, self, _node, content_id).__init__()
    self.content_positions = {}  # コンテンツを保存しているノード


class data_packet(packet):
  def __init__(self, _node, content_id):
    super(packet, self, _node, content_id).__init__()
    self.user_position = None
    self.data = 0
    self.max_data = 64  # 64[Kb]
