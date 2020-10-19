# Physarum Solverの計算
'''
参考文献:
[Pythonで粘菌ネットワーク](https://qiita.com/STInverSpinel/items/8ced06ea7881613a3e2c)
'''
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

G = nx.Graph()
G.add_nodes_from([0, 1, 2, 3, 4])
G.add_edges_from([(0, 2), (0, 3), (2, 3), (2, 4), (1, 4), (1, 3), (3, 4)])
pos = nx.spring_layout(G)

# 変数宣言
nt = 13
# 今回はdt=1とする
nnodes = nx.number_of_nodes(G)
edge_list = list(G.edges)
nbr_mtx = nx.to_numpy_matrix(G)

conductivity = np.zeros((nt, nnodes, nnodes))  # D
length = np.zeros((nnodes, nnodes))  # L
pressure = np.zeros((nt, nnodes))  # p
flux = np.zeros(nnodes)  # Q

# 初期値と定数の設定
conductivity[0] = nbr_mtx  # 各エッジの流れやすさは最初1.0
length = nbr_mtx  # 今回は各エッジの長さは1.0とする
I0 = 2.0
flux[0] = I0
flux[1] = -I0
gamma = 1.8

# ゼロ除算が発生しないように非ゼロ要素のみで割り算を行う


def divide_non_zero_element(D, L, num_nodes, list_edges):
  X = np.zeros((num_nodes, num_nodes))
  for i, j in list_edges:
    X[i, j] = D[i, j] / L[i, j]
    X[j, i] = D[j, i] / L[j, i]
  return X

# f(Q) for dD/dt


def f(x):
  powered = x**gamma
  return powered / (powered + 1)

# Dの時間変化量を求める


def dD(D, L, p, num_nodes, list_edges):
  X = divide_non_zero_element(D, L, num_nodes, list_edges)
  Q = np.multiply(X, np.expand_dims(p, axis=1) - p)
  ans = f(np.abs(Q))
  return ans

# 一次連立方程式を解きpを求める


def deduce_p(D, L, B, num_nodes, list_edges):
  Y = divide_non_zero_element(D, L, num_nodes, list_edges)
  A = np.diag(np.sum(Y, axis=1)) - Y
  p = np.linalg.solve(A, B)
  return p


# pの初期値を求める
pressure[0] = deduce_p(conductivity[0], length, flux, nnodes, edge_list)

# 繰り返し計算する
for t in range(0, nt - 1):
  conductivity[t + 1] = dD(conductivity[t], length, pressure[t], nnodes, edge_list)
  pressure[t + 1] = deduce_p(conductivity[t + 1], length, flux, nnodes, edge_list)

fig = plt.figure()

datatype = [('conductivity', float)]


def animate(i):
  A = np.matrix(conductivity[i], dtype=datatype)
  G = nx.from_numpy_matrix(A)
  weights = [G[u][v]['conductivity'] for u, v in G.edges()]

  plt.cla()
  nx.draw_networkx(G, pos, width=weights)
  plt.axis('off')
  plt.title('t=' + str(i))
  # plt.show()


anim = FuncAnimation(fig, animate, frames=nt, repeat=True)
anim.save("Export/nenkin01.gif", writer='pillow', fps=6)
plt.show()
