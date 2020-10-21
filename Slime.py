from scipy.spatial import distance
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
    length_d = distance.euclidean(self.node.position, self.node.content_position)
    length_neighbors = []
    length_neighbors2d = []
    for neighbor in self.node.neighbor:
      length_neighbor = distance.euclidean(self.node.position, neighbor.position)
      length_neighbor2d = distance.euclidean(neighbor.position, self.node.content_position)
      length_neighbors.append(length_neighbor)
      length_neighbors2d.append(length_neighbor2d)
      s = self.solve_s(length_d, length_neighbor, length_neighbor2d)
      area = self.solve_area(s, length_d, length_neighbor, length_neighbor2d)
      h = self.solve_h(area, length_d)
      theta_neighbor = self.solve_theta_neighbor(h, length_neighbor2d)
      self.theta_neighbors.append(theta_neighbor)

      # x = (length_neighbor * length_neighbor + length_d * length_d - length_neighbor2d * length_neighbor2d) / 2 * length_neighbor * length_d
      # theta_neighbor = np.arccos(x - int(x))
      # self.theta_neighbors.append(theta_neighbor)
      length_neighbor_dash = length_neighbor / np.cos(theta_neighbor)
      length_neighbor_dash2d = length_d - length_neighbor_dash
      self.length.append(length_neighbor_dash2d / length_d)

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
