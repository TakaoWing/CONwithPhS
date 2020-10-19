#!/Users/tsubasatakaoka/Desktop/CONwithPhS/.venv/bin/python
# -*- coding: utf-8 -*-

'''
Main: 実験の処理を行う
'''
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# my classes
from node import node


def create_nodes(max_nodes):
  nodes = []
  for i in range(max_nodes):
    nodes.append(node())
  return nodes


def set_matrix(nodes, root_max_nodes):
  for i in range(root_max_nodes):
    for j in range(root_max_nodes):
      nodes[j + i * root_max_nodes].position = (i, j)
  return nodes


def get_nodes_position(nodes):
  nodes_position = []
  for _node in nodes:
    nodes_position.append(_node.position)
  return nodes_position


def main():
  MAX_NODES = 100
  ROOT_MAX_NODES = int(np.sqrt(MAX_NODES))

  nodes = create_nodes(MAX_NODES)
  set_matrix(nodes, ROOT_MAX_NODES)

  nodes_position = get_nodes_position(nodes)
  dict_nodes_position = dict(zip(nodes, nodes_position))

  G = nx.Graph()
  G.add_nodes_from(nodes)

  nx.draw_networkx_nodes(G, nodes, dict_nodes_position, node_size=10, alpha=1, node_color="blue")

  plt.show()


if __name__ == "__main__":
  main()
