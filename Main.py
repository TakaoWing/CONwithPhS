#!/Users/tsubasatakaoka/Desktop/CONwithPhS/.venv/bin/python
# -*- coding: utf-8 -*-

'''
Main: 実験の処理を行う
'''
import networkx as nx
import matplotlib.pyplot as plt
# import numpy as np
import random
from matplotlib.animation import FuncAnimation

# my classes
from node import node


def create_nodes(max_nodes):
  nodes = []
  for i in range(max_nodes):
    nodes.append(node(i))
  return nodes


def set_matrix(nodes, root_max_nodes):
  for i in range(root_max_nodes):
    for j in range(root_max_nodes):
      nodes[j + i * root_max_nodes].position = (i, j)
  return nodes


def set_random(nodes):
  for _node in nodes:
    _node.position = (random.uniform(0, 400), random.uniform(0, 400))
  return nodes


def get_nodes_position(nodes):
  nodes_position = []
  for _node in nodes:
    nodes_position.append(_node.position)
  return dict(zip(nodes, nodes_position))


def get_nodes_link(nodes):
  nodes_link = []
  for _node in nodes:
    _node.send_hello(nodes)
    for neighbor in _node.neighbor:
      nodes_link.append((_node, neighbor))
  return nodes_link


def nodes_move(nodes):
  for _node in nodes:
    _node.move()


def main():
  MAX_NODES = 100
  # ROOT_MAX_NODES = int(np.sqrt(MAX_NODES))

  nodes = create_nodes(MAX_NODES)
  # set_matrix(nodes, ROOT_MAX_NODES)
  # ノードに偏りが生じないように分散させたい！
  set_random(nodes)

  fig = plt.figure(figsize=(10, 10))

  def animate(i):
    plt.cla()
    nodes_position = get_nodes_position(nodes)
    nodes_link = get_nodes_link(nodes)

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(nodes_link)

    nx.draw_networkx_nodes(G, nodes_position, node_size=30, alpha=1, node_color="blue")
    nx.draw_networkx_edges(G, nodes_position, label=1, edge_color="black", width=2)
    plt.axis('off')
    plt.title("t=" + str(i))
    # グラフの保存
    # plt.savefig("Export/netork.png")

    # グラフの表示
    # plt.show()
    nodes_move(nodes)

  anim = FuncAnimation(fig, animate, frames=t, interval=10, repeat=True)
  anim.save("Export/SaveAnimaiton.gif", writer="imagemagick", fps=fps)


if __name__ == "__main__":
  fps = 30
  t = 200
  random.seed(0)
  main()
