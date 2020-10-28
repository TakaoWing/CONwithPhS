import numpy as np
from numpy import linalg as LA


def tangent_angle(u: np.ndarray, v: np.ndarray):
  i = np.inner(u, v)
  n = LA.norm(u) * LA.norm(v)
  c = i / n
  return np.rad2deg(np.arccos(np.clip(c, -1.0, 1.0)))


Ax, Ay = 369, 337
Bx, By = 364, 393
Cx, Cy = 364, 213

# a = np.array([3, 4])
# b = np.array([-4, 3])

# a = np.array([Ax - Bx, Ay - By]) # node 8 の時
# b = np.array([Cx - Bx, Cy - By]) # node 8 の時

a = np.array([Bx - Ax, By - Ay])  # node 39 の時
b = np.array([Cx - Ax, Cy - Ay])  # node 39 の時

print(tangent_angle(a, b))
# 90.0
