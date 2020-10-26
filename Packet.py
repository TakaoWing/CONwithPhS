

class packet:
  def __init__(self, _node):
    self.living_time = 0  # 生存時間
    self.TTL = 20  # 生存可能時間
    self.content_id = ""  # コンテンツID
    self.content_positions = {}  # コンテンツを保存しているノード
    self.position_node = _node  # packetの現在地
    self.trace = []  # 辿った経路
