
from scipy.spatial import distance
import random


class position:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.vector = (self.x, self.y)

  def set_vector(self, x, y):
    self.x = x
    self.y = y
    self.vector = (self.x, self.y)

  def get_vector(self):
    self.vector = (self.x, self.y)
    return self.vector

  def move(self):
    speed = 3.0
    self.x += random.uniform(-speed, speed)
    self.y += random.uniform(-speed, speed)

  def distance(self, other_position):
    return distance.euclidean(self.get_vector(), other_position.get_vector())
