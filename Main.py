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

# my classess
from node import node
from node import content


def create_nodes(max_nodes):  # ノードの作成
  nodes = []  # ノードの初期化
  # 最大ノード数だけノードを生成
  for i in range(max_nodes):
    nodes.append(node(i))
  return nodes


def set_matrix(nodes, root_max_nodes):  # ノードを格子状に配置
  for i in range(root_max_nodes):
    for j in range(root_max_nodes):
      nodes[j + i * root_max_nodes].position.set_vector(i, j)
  return nodes


def set_random(nodes, field_size):  # ノードをランダムを広さ(diled_size)上に配置
  for _node in nodes:
    _node.position.set_vector(random.uniform(0, field_size), random.uniform(0, field_size))
  return nodes


def get_nodes_position(nodes):  # ノードの場所を辞書型配列{ノード,ノードの場所}を返す
  nodes_position = [_node.position for _node in nodes]
  return dict(zip(nodes, nodes_position))


def get_nodes_link(nodes):  # ノード同士が接続関係を配列で返す
  nodes_link = []
  for _node in nodes:
    _node.send_hello(nodes)
    for neighbor in _node.neighbor:
      nodes_link.append((_node, neighbor))
  return nodes_link


def get_nodes_color(nodes):  # ノードの色をコンテンツを保持しているか，コンテンツを要求しているかで指定し配列で返す
  nodes_color = []
  for _node in nodes:
    if len(_node.content_store) != 0:
      nodes_color.append("red")
    elif _node.want_content != "":
      nodes_color.append("green")
    else:
      nodes_color.append("blue")

  return nodes_color


def get_nodes_name(nodes):  # ノードの名前を辞書型配列で返す
  nodes_name = [_node.number for _node in nodes]
  return dict(zip(nodes, nodes_name))


def nodes_move(nodes):  # nodeの動きをまとめて実装
  for _node in nodes:
    _node.move()


def main():
  MAX_NODES = 100  # ノードを数を設定
  nodes = create_nodes(MAX_NODES)  # max_nodesだけノードを生成

  # コンテンツ保持端末とコンテンツ要求端末をランダムで決定する
  have_content_node = random.randint(0, MAX_NODES)
  nodes[have_content_node].content_store.append(content(content_id="www.google.com/logo.png", data_size=10000))
  want_content_node = random.randint(0, MAX_NODES)
  nodes[want_content_node].want_content = "www.google.com/logo.png"
  nodes[want_content_node].content_position = nodes[have_content_node].position

  # ノードに偏りが生じないように分散させたい！
  set_random(nodes=nodes, field_size=400)

  fig = plt.figure(figsize=(20, 20))

  def animate(i):
    plt.cla()
    nodes_position = get_nodes_position(nodes)
    nodes_link = get_nodes_link(nodes)
    nodes_color = get_nodes_color(nodes)
    nodes_name = get_nodes_name(nodes)
    nodes[want_content_node].select_next()
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(nodes_link)

    nx.draw_networkx_nodes(G, nodes_position, node_size=400, alpha=1, node_color=nodes_color)
    nx.draw_networkx_edges(G, nodes_position, label=1, edge_color="black", width=2)
    nx.draw_networkx_labels(G, nodes_position, nodes_name, font_size=10, font_color="white")
    plt.axis('off')
    plt.title("t=" + str(i))
    # グラフの保存
    # plt.savefig("Export/netork.png")

    # グラフの表示
    # plt.show()
    nodes_move(nodes)

  animate(0)
  anim = FuncAnimation(fig, animate, frames=t, interval=10, repeat=True)
  anim.save("Export/SaveAnimaiton.gif", writer="imagemagick", fps=fps)


if __name__ == "__main__":
  fps = 30
  t = 20
  random.seed(0)
  main()
