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
from con.node import node
from con.node import content


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
  nodes_position = [_node.position.get_vector() for _node in nodes]
  return dict(zip(nodes, nodes_position))


def get_nodes_link(nodes):  # ノード同士が接続関係を配列で返す
  nodes_link = []
  for _node in nodes:
    _node.connect_links(nodes)
    for neighbor in _node.neighbor:
      nodes_link.append((_node, neighbor))
  return nodes_link


def get_nodes_color(nodes):  # ノードの色をコンテンツを保持しているか，コンテンツを要求しているかで指定し配列で返す
  nodes_color = []
  for _node in nodes:
    if len(_node.content_store) != 0:
      nodes_color.append("red")
    elif _node.request_content_id != "":
      nodes_color.append("green")
    else:
      nodes_color.append("blue")

  return nodes_color


def get_nodes_name(nodes):  # ノードの名前を辞書型配列で返す
  nodes_name = [_node.number for _node in nodes]
  return dict(zip(nodes, nodes_name))


def get_eges_color(edges, edges_communication):
  edges_color = []
  for edge_from, edge_to in edges:
    color = "black"
    for edge_c_from, edge_c_to in edges_communication:
      if edge_from is edge_c_from and edge_to is edge_c_to:
        color = "red"
    edges_color.append(color)

  return edges_color


def nodes_move(nodes):  # nodeの動きをまとめて実装
  for _node in nodes:
    _node.move()


def main():
  MAX_NODES = 100  # ノードを数を設定
  nodes = create_nodes(MAX_NODES)  # max_nodesだけノードを生成

  # ノードに偏りが生じないように分散させたい！
  set_random(nodes=nodes, field_size=400)

  # コンテンツ保持端末とコンテンツ要求端末をランダムで決定する
  have_content_node = random.randint(0, MAX_NODES)
  nodes[have_content_node].content_store.append(content(content_id="www.google.com/logo.png", data_size=10000))
  want_content_node = random.randint(0, MAX_NODES)
  nodes[want_content_node].set_packet("www.google.com/logo.png", nodes[have_content_node].position)
  nodes[want_content_node].request_content_id = "www.google.com/logo.png"
  want_content_node = 50
  nodes[want_content_node].set_packet("www.google.com/logo.png", nodes[have_content_node].position)
  nodes[want_content_node].request_content_id = "www.google.com/logo.png"
  # want_content_node = 71
  # nodes[want_content_node].set_packet("www.google.com/logo.png", nodes[have_content_node].position)
  # nodes[want_content_node].request_content_id = "www.google.com/logo.png"
  # want_content_node = 93
  # nodes[want_content_node].set_packet("www.google.com/logo.png", nodes[have_content_node].position)
  # nodes[want_content_node].request_content_id = "www.google.com/logo.png"

  fig = plt.figure(figsize=(20, 20))

  def animate(i):
    plt.cla()
    nodes_position = get_nodes_position(nodes)
    nodes_link = get_nodes_link(nodes)
    nodes_color = get_nodes_color(nodes)
    nodes_name = get_nodes_name(nodes)
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(nodes_link)

    loop_count = node.que.qsize()

    edges_communication = []
    for c in range(loop_count):
      _node = node.que.get()
      print("Node{} process packet-protocol".format(_node.number))
      _node.packet_protocol(nodes)
      for n in _node.select_next_node:
        print("Node{} → Node{}".format(_node.number, n.number))
        edges_communication.append((_node, n))
        edges_communication.append((n, _node))

    edges_color = get_eges_color(nodes_link, edges_communication)

    nx.draw_networkx_nodes(G, nodes_position, node_size=400, alpha=1, node_color=nodes_color)
    nx.draw_networkx_edges(G, nodes_position, label=1, edge_color=edges_color, width=2)
    nx.draw_networkx_labels(G, nodes_position, nodes_name, font_size=10, font_color="white")
    plt.axis('off')
    plt.title("t=" + str(i))
    # グラフの保存
    plt.savefig("Export/netork.png")

    # グラフの表示
    # plt.show()
    # nodes_move(nodes)

  # animate(0)
  # return
  anim = FuncAnimation(fig, animate, frames=t, interval=10, repeat=True)
  anim.save("Export/SaveAnimaiton.gif", writer="imagemagick", fps=fps)


if __name__ == "__main__":
  fps = 30
  t = 20
  random.seed(0)
  main()
