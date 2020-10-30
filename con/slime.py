
import numpy as np
from numpy import linalg as LA


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

  def solve_s(self, a, b, c):
    return (a + b + c) / 2

  def solve_area(self, s, a, b, c):
    return np.sqrt(s * (s - a) * (s - b) * (s - c))

  def solve_h(self, area, a):
    return 2 * area / a

  def solve_theta_neighbor(self, h, c):
    return np.arcsin(h / c)

  def tangent_angle(self, u: np.ndarray, v: np.ndarray):
    i = np.inner(u, v)
    n = LA.norm(u) * LA.norm(v)
    c = i / n
    return np.arccos(np.clip(c, -1.0, 1.0))  # np.rad2deg(np.arccos(np.clip(c, -1.0, 1.0)))

  def solve_length(self, neighbor, length_d):

    vector_me = self.node.position.get_vector()
    vector_neighbor = neighbor.position.get_vector()
    vector_distination = self.node.packet.content_positions.get_vector()

    vector_me2neighbor = list(map(lambda vec1, vec2: vec1 - vec2, vector_me, vector_neighbor))
    vector_me2d = list(map(lambda vec1, vec2: vec1 - vec2, vector_me, vector_distination))
    # vector_neighbor2d = list(map(lambda vec1, vec2: vec1 - vec2, vector_neighbor, vector_distination))

    a = np.array(vector_me2neighbor)
    b = np.array(vector_me2d)

    length_neighbor = self.node.position.distance(neighbor.position)  # length_neighbor:自分自身と接続されたノードまでの距離
    # length_neighbor2d = neighbor.position.distance(self.node.packet.content_positions)  # length_neighbor2d:neighborからコンテンツ保持端末までの距離

    # s = self.solve_s(length_d, length_neighbor, length_neighbor2d)  # s:自身とneighborとコンテンツ保持端末を結んだ３角形の周りの長さの半分
    # area = self.solve_area(s, length_d, length_neighbor, length_neighbor2d)  # area:３角形の面積
    # h = self.solve_h(area, length_d)  # h: 三角形の高さ
    # theta_neighbor = self.solve_theta_neighbor(h, length_neighbor2d)  # 三角形の角度
    theta_neighbor = self.tangent_angle(a, b)
    length_neighbor_dash = length_neighbor / np.cos(theta_neighbor)  # 自身とneighborまでの投影距離
    length_neighbor_dash2d = length_d - length_neighbor_dash  # neighorとコンテンツまでの投影距離
    length = length_neighbor_dash2d / length_d
    return length, theta_neighbor

  def solve_init_d(self, pressure):
    conductivitiy = (pressure - self.P_MIN) / (self.P_MAX - self.P_MIN)
    return conductivitiy

  def solve_d(self, conductivity, growth_rate):
    conductivity += self.dt * (growth_rate - self.gamma * conductivity)
    return conductivity

  def growth_rate(self, quantity):
    rate = abs(quantity) / sum(abs(value) for value in self.quantities.values())
    return rate

  def solve_delta_p(self, neighbor):
    pressure = self.alpha * neighbor.energy + self.beta * neighbor.buffer
    return pressure

  def solve_q(self, conductivity, pressure, length):
    quantity = conductivity * pressure / length
    return quantity

  def init_physarum_solver(self):
    self.length = {}
    self.theta_neighbors = {}
    self.pressures = {}
    self.conductivities = {}
    length_d = self.node.position.distance(self.node.packet.content_positions)  # length_d:自分自身とコンテンツ保持端末までの距離
    for neighbor in self.node.neighbor:  # neighbor:接続されたノード
      length, theta_neighbor = self.solve_length(neighbor, length_d)  # 投影距離の計算 L_ij
      pressure_neighbor = self.solve_delta_p(neighbor)  # 圧力差の計算 dp_ij
      conductivity_neighbor = self.solve_init_d(pressure_neighbor)  # 伝導率の初期値の計算 D_ij
      quantity_neighbor = self.solve_q(conductivity_neighbor, pressure_neighbor, length)  # 流量の計算 Q_ij
      self.theta_neighbors[neighbor] = theta_neighbor  # 角度をtheta_neighborsに格納
      self.length[neighbor] = length  # 菅の長さ(L_j'd/L_id)をlengthに格納
      self.pressures[neighbor] = pressure_neighbor
      self.conductivities[neighbor] = conductivity_neighbor
      self.quantities[neighbor] = quantity_neighbor
    return

  def physarum_solver(self):
    self.length = {}
    self.theta_neighbors = {}
    self.pressures = {}
    length_d = self.node.position.distance(self.node.packet.content_positions)  # length_d:自分自身とコンテンツ保持端末までの距離
    for neighbor in self.node.neighbor:  # neighbor:接続されたノード
      length, theta_neighbor = self.solve_length(neighbor, length_d)  # 投影距離の計算 L_ij
      pressure_neighbor = self.solve_delta_p(neighbor)  # 圧力差の計算 dp_ij
      growth_rate_neighbor = self.growth_rate(self.quantities[neighbor])  # 成長率の計算 f(|Qij|)
      conductivity_neighbor = self.solve_d(self.conductivities[neighbor], growth_rate_neighbor)  # 伝導率の計算 D_ij
      quantity_neighbor = self.solve_q(conductivity_neighbor, pressure_neighbor, length)  # 流量の計算 Q_ij
      self.theta_neighbors[neighbor] = theta_neighbor  # 角度をtheta_neighborsに格納
      self.length[neighbor] = length  # 菅の長さ(L_j'd/L_id)をlengthに格納
      self.pressures[neighbor] = pressure_neighbor
      self.conductivities[neighbor] = conductivity_neighbor
      self.quantities[neighbor] = quantity_neighbor
    return
