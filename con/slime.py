
import numpy as np
from numpy import linalg as LA
import math


class tube:  # ノード間を繋ぐ粘菌のチューブ
  def __init__(self):
    self.quantity = 0
    self.conductivity = 0
    self.pressure = 0
    self.length = 0
    self.theta_neighbor = 0


class slime:
  def __init__(self, _node):
    # conductivitiesはD[n]を求めるためにD[n-1]を用いるため,conductivies[1] = D[n-1], conductivies[0] = D[n]となるような構造に変更する．
    # conductivies[1][nodes(neighbers)]となる構造体である．
    self.conductivities = {}  # 自身と接続されたノード間の伝導率の値，D_ij，ネットワーク固有の物理的徳衛 D_ijの初期値には，リンク品質を用いる
    # pressures[nodes(neighbers)]となる構造体である．
    self.pressures = {}  # 自身と接続されたノード間の圧力差, dP_ij，リンク品質
    self.quantities = {}  # 自身と接続されたノード間の流量，Q_ij，
    self.length = {}  # 自身と接続されたノード間の長さ，L_ij，物理的な距離とはことなる．自身とコンテンツまでの直線距離から接続されたノードの投影距離である．
    self.node = _node  # nodeの情報を取得
    self.alpha = 0.62  # dP_ijの値を決定する係数 nodeのエネルギー残量の係数
    self.beta = 0.38  # dP_ijの値を決定する係数 nodeのバッファ残量の係数
    self.gamma = 0.5  # 収縮率
    self.P_MAX = 1.0  # 通信できる最大電力 node固有の値
    self.P_MIN = 0.1  # 通信できる最小電力 node固有の値
    # theta_neighbors[nodes(neighobrs)]となる構造体である．
    self.theta_neighbors = {}  # 接続されたノード，自身，コンテンツからなるなす角
    self.dt = 0.1  # 本来であれば，pps[packets per second]の逆数の値, max(dt) = 0.1となる
    self.tubes = {}

  def tangent_angle(self, u: np.ndarray, v: np.ndarray):
    """
    2つのベクトル からなす角を取得する．

    Parameters
    ----------
    u : np.ndarray
      対象のベクトル
    v : np.ndarray
      対象のベクトル

    Returns
    -------
    なす角（ラジアン）
    """
    i = np.inner(u, v)
    n = LA.norm(u) * LA.norm(v)
    c = i / n
    return np.arccos(np.clip(c, -1.0, 1.0))  # np.rad2deg(np.arccos(np.clip(c, -1.0, 1.0)))

  def solve_length(self, neighbor, length_d):
    """
    ノードから隣接ノードまでの長さを計算

    Parameters
    ----------
    neighbor : node
      隣接ノード
    length_d : float
      ノードからコンテンツ保持端末までの距離

    Returns
    -------
    length : float
      ノードから隣接ノードまでの長さ
    theta_neighbor : float
      ノードと隣接ノードとコンテンツ保持端末のなす角
    """

    vector_me = self.node.position.get_vector()  # vector_me : 自身のベクトル　memo : 変わらないからここで計算しないこと！
    vector_neighbor = neighbor.position.get_vector()  # vector_neighbor : 隣接ノードのベクトル
    vector_distination = self.node.packet.content_positions.get_vector()  # vector_disination : コンテンツ保持端末のベクトル memo : 変わらないからここで計算しないこと！

    vector_me2neighbor = list(map(lambda vec1, vec2: vec1 - vec2, vector_me, vector_neighbor))  # vector_me2neighbor : 自身の座標を原点とした隣接ノードのベクトル
    vector_me2d = list(map(lambda vec1, vec2: vec1 - vec2, vector_me, vector_distination))  # vector_me2d : 自身の座標を原点としたコンテンツ保持端末のベクトル
    theta_neighbor = self.tangent_angle(np.array(vector_me2neighbor), np.array(vector_me2d))  # theta_neighbor : vector_me2neighborとvector_me2dのなす角

    length_neighbor = self.node.position.distance(neighbor.position)  # length_neighbor : 自分自身と隣接ノードまでの距離
    length_neighbor_dash = length_neighbor * np.cos(theta_neighbor)  # length_neighbor_dash : 自身とコンテンツ保持端末におけるneighborの投影距離
    length_neighbor_dash2d = length_d - length_neighbor_dash  # length_neighbor_dash2d : neighorとコンテンツまでの投影距離
    length = length_neighbor_dash2d / length_d + 1e-25  # length : ノードと隣接ノードの距離 1e-25はゼロ除算対策

    return length, math.degrees(theta_neighbor)

  def solve_init_d(self, pressure):
    conductivitiy = (pressure - self.P_MIN) / (self.P_MAX - self.P_MIN)
    return conductivitiy

  def solve_d(self, conductivity, growth_rate):
    conductivity += self.dt * (growth_rate - self.gamma * conductivity)
    return conductivity

  def growth_rate(self, quantity):
    rate = abs(quantity) / sum(abs(value.quantity) for value in self.tubes.values())
    return rate

  def solve_delta_p(self, neighbor):
    pressure = self.alpha * neighbor.energy + self.beta * neighbor.buffer
    return pressure

  def solve_q(self, conductivity, pressure, length):
    quantity = conductivity * pressure / length
    return quantity

  def init_tube(self, neighbor, length_d):
    _tube = tube()
    _tube.length, _tube.theta_neighbor = self.solve_length(neighbor, length_d)  # 投影距離の計算 L_ij
    _tube.pressure = self.solve_delta_p(neighbor)  # 圧力差の計算 dp_ij
    _tube.conductivity = self.solve_init_d(_tube.pressure)  # 伝導率の初期値の計算 D_ij
    _tube.quantity = self.solve_q(_tube.conductivity, _tube.pressure, _tube.length)  # 流量の計算 Q_ij
    return _tube

  def physarum_solver(self):
    length_d = self.node.position.distance(self.node.packet.content_positions)  # length_d:自分自身とコンテンツ保持端末までの距離
    for neighbor in self.node.neighbor:  # 初めて接続されたノードに対して，チューブの初期化を行う．
      if neighbor in self.tubes:
        continue
      self.tubes[neighbor] = self.init_tube(neighbor, length_d)
    for neighbor in self.node.neighbor:  # neighbor:接続されたノード
      if neighbor not in self.tubes:  # 初めて接続されたノードは以下の処理を実行しない
        continue
      _tube = self.tubes[neighbor]
      _tube.length, _tube.theta_neighbor = self.solve_length(neighbor, length_d)  # 投影距離の計算 L_ij
      _tube.pressure = self.solve_delta_p(neighbor)  # 圧力差の計算 dp_ij
      growth_rate_neighbor = self.growth_rate(_tube.quantity)  # 成長率の計算 f(|Qij|)
      _tube.conductivity = self.solve_d(_tube.conductivity, growth_rate_neighbor)  # 伝導率の計算 D_ij
      _tube.quantity = self.solve_q(_tube.conductivity, _tube.pressure, _tube.length)  # 流量の計算 Q_ij
    return

  def get_quantities(self):
    quantities = {}
    for tube_key, tube_value in self.tubes.items():
      quantities[tube_key] = tube_value.quantity
    return quantities
