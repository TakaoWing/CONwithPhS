import random


class packet:
  """
  ネットワークにおける端末同士の情報のやり取り際に用いられるデータ
  """

  def __init__(self, content_id):
    self.living_time = 0  # 生存時間
    self.ttl = 20  # 生存可能時間
    self.content_id = content_id  # コンテンツID
    self.trace = []  # 辿った経路
    self.randam_bin = format(random.randint(0, 255), '08b')

  def is_living(self):
    print("packet::ContentID:{},TTL:{}".format(self.content_id, self.living_time))
    return self.living_time > self.ttl


class interest_packet(packet):
  """
  ユーザがコンテンツを要求する際に送信するパケット
  コンテンツ保持端末の位置情報を持っている．
  """

  def __init__(self, content_id, content_positions=None):
    super().__init__(content_id)
    self.content_positions = content_positions if content_positions else []  # コンテンツを保存しているノード


class data_packet(packet):
  """
  interestパケットに応答するパケット
  ユーザの位置情報を持たない．
  """

  def __init__(self, _node, content_id, data_size=None, max_number=None, number=None, user_positions=None):
    super().__init__(content_id)
    self.user_positions = user_positions if user_positions else []  # ノードのpitを元に経路選択されるため，必要ではない，しかし，最適経路を選択する上では必要かも
    self.data_size = data_size  # 自身のデータサイズ [byte]
    self.max_number = max_number
    self.number = number


class slime_interest_packet(packet):
  """
  粘菌アルゴリズム用のパケット
  ユーザがコンテンツを要求する際に送信されるパケット
  コンテンツ保持端末の位置情報を持たない．
  """

  def __init__(self, content_id):
    super().__init__(content_id)


class slime_data_packet(packet):
  """
  粘菌アルゴリズム用のパケット
  slime-interestパケットに応答する際に送信されるパケット
  コンテンツ保持端末の位置情報を持っている
  """

  def __init__(self, content_id, content_position=None):
    super().__init__(content_id)
    self.content_position = content_position
