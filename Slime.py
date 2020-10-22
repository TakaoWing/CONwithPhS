
import numpy as np


class slime:
  def __init__(self, _node):
    self.conductivities = {}
    self.pressures = []
    self.quantities = {}
    self.length = []
    self.node = _node
    self.alpha = 0.62
    self.beta = 0.38
    self.P_MAX = 1.0
    self.P_MIN = 0.1
    self.theta_neighbors = []

  def solve_s(self, a, b, c):
    return (a + b + c) / 2

  def solve_area(self, s, a, b, c):
    return np.sqrt(s * (s - a) * (s - b) * (s - c))

  def solve_h(self, area, a):
    return 2 * area / a

  def solve_theta_neighbor(self, h, c):
    return np.arcsin(h / c)

  def solve_length(self):
    if self.node.want_content == "":
      return
    self.length = []
    self.theta_neighbors = []
    self.pressures = []
    self.conductivityes = []
    length_d = self.node.position.distance(self.node.content_position)  # length_d:自分自身とコンテンツ保持端末までの距離
    for neighbor in self.node.neighbor:  # neighbor:接続されたノード
      length_neighbor = self.node.position.distance(neighbor.position)  # length_neighbor:自分自身と接続されたノードまでの距離
      length_neighbor2d = neighbor.position.distance(self.node.content_position)  # length_neighbor2d:neighborからコンテンツ保持端末までの距離

      s = self.solve_s(length_d, length_neighbor, length_neighbor2d)  # s:自身とneighborとコンテンツ保持端末を結んだ３角形の周りの長さの半分
      area = self.solve_area(s, length_d, length_neighbor, length_neighbor2d)  # area:３角形の面積
      h = self.solve_h(area, length_d)  # h: 三角形の高さ
      theta_neighbor = self.solve_theta_neighbor(h, length_neighbor2d)  # 三角形の角度
      length_neighbor_dash = length_neighbor / np.cos(theta_neighbor)  # 自身とneighborまでの投影距離
      length_neighbor_dash2d = length_d - length_neighbor_dash  # neighorとコンテンツまでの投影距離
      length = length_neighbor_dash2d / length_d

      pressure_neighbor = self.alpha * neighbor.energy + self.beta * neighbor.buffer

      conductivitiy_neighbor = (pressure_neighbor - self.P_MIN) / (self.P_MAX - self.P_MIN)

      quantity_neighbor = conductivitiy_neighbor * pressure_neighbor / length

      # データの格納
      self.theta_neighbors.append(theta_neighbor)  # 角度をtheta_neighborsに格納
      self.length.append(length)  # 菅の長さ(L_j'd/L_id)をlengthに格納
      self.pressures.append(pressure_neighbor)
      self.conductivities.append(conductivitiy_neighbor)
      self.quantities.append(quantity_neighbor)
    return

  def init_d(self):
    self.conductivities = []
    for pressure in self.pressures:
      self.conductivities.append((pressure - self.P_MIN) / (self.P_MAX - self.P_MIN))
    return

  def delta_d(self):
    print("dD")
    return

  def delta_p(self):
    self.pressures = []
    for neighbor in self.node.neighbor:
      self.pressures.append(self.alpha * neighbor.energy + self.beta * neighbor.buffer)
    return

  def solve_q(self):
    quantity_list = []
    for i in range(len(self.node.neighbor)):
      quantity_list.append(self.conductivities[i] * self.pressures[i] / self.length[i])
    self.quantities = dict(zip(self.node.neighbor, quantity_list))
    return

  def physarum_solver(self):
    self.delta_p()
    self.init_d()
    self.solve_q()

    return
