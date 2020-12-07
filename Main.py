#!/Users/tsubasatakaoka/Desktop/CONwithPhS/.venv/bin/python
# -*- coding: utf-8 -*-

'''
Main: 実験の処理を行う
'''
import networkx as nx
import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation
import queue

# my classess
from con.slime_node import slime_node
from con.pbr_node import pbr_node
from con.content import content


def create_slime_nodes(max_nodes):  # ノードの作成
  nodes = []  # ノードの初期化
  # 最大ノード数だけノードを生成
  for i in range(max_nodes):
    nodes.append(slime_node(i))
  return nodes


def create_pbr_nodes(max_nodes):  # ノードの作成
  nodes = []  # ノードの初期化
  # 最大ノード数だけノードを生成
  for i in range(max_nodes):
    nodes.append(pbr_node(i))
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
      if neighbor.number < _node.number:
        continue
      nodes_link.append((_node, neighbor))
  return nodes_link


def get_nodes_color(nodes):  # ノードの色をコンテンツを保持しているか，コンテンツを要求しているかで指定し配列で返す
  nodes_color = []
  for _node in nodes:
    if len(_node.content_store) != 0:
      nodes_color.append("red")
    elif _node.request_content:
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
    for edge_c_from, edge_c_to, packet_type in edges_communication:
      if edge_from is edge_c_from and edge_to is edge_c_to:
        if packet_type == "<class 'con.packet.interest_packet'>":
          color = "green"
        elif packet_type == "<class 'con.packet.data_packet'>":
          color = "red"
        elif packet_type == "<class 'con.packet.slime_interest_packet'>" or packet_type == "<class 'con.packet.advertise_packet'>":
          color = "orange"
        elif packet_type == "<class 'con.packet.slime_data_packet'>":
          color = "pink"

    edges_color.append(color)

  return edges_color


def get_file_name(nodes):
  file_name = "User("
  for i, _node in enumerate(nodes):
    if not _node.request_content:
      continue
    file_name += str(_node.number)
    file_name += ","
  file_name = file_name[:-1]
  file_name += ")"
  file_name += "2"
  file_name += "Content("
  for i, _node in enumerate(nodes):
    if not _node.content_store:
      continue
    file_name += str(_node.number)
    file_name += ","
  file_name = file_name[:-1]
  file_name += ")"
  return file_name


def nodes_move(nodes):  # nodeの動きをまとめて実装
  for _node in nodes:
    _node.move()
  return


def create_graph(name, x, y):
  plt.cla()
  plt.tick_params(bottom=True,
                  left=True,
                  right=False,
                  top=False)
  plt.tick_params(labelbottom=True,
                  labelleft=True,
                  labelright=False,
                  labeltop=False)
  plt.plot(y, x)
  plt.xlabel("Unit Time", fontsize=24)
  plt.ylabel("Traffic", fontsize=24)
  plt.savefig("Export/{}.png".format(name))
  return


def main(protocol):

  MAX_NODES = 100  # ノードを数を設定
  if protocol == "slime":
    nodes = create_slime_nodes(MAX_NODES)  # max_nodesだけノードを生成
  elif protocol == "pbr":
    nodes = create_pbr_nodes(MAX_NODES)
  else:
    print("Don't set protocol!!")
    return

  # ノードに偏りが生じないように分散させたい！
  set_random(nodes=nodes, field_size=400)

  # コンテンツ保持端末とコンテンツ要求端末をランダムで決定する
  have_content_node = random.randint(0, MAX_NODES)
  nodes[have_content_node].set_content(content(content_id="www.google.com/logo.png", data_size=10000))
  # nodes[have_content_node].content_store["www.google.com/logo2.png"] = content(content_id="www.google.com/logo2.png", data_size=10000)
  # have_content_node = 63
  # nodes[have_content_node].content_store.append(content(content_id="www.google.com/logo2.png", data_size=10000))
  # want_content_node = random.randint(0, MAX_NODES)
  # nodes[want_content_node].set_packet("www.google.com/logo.png", nodes[have_content_node].position)
  # want_content_node = 47
  # nodes[want_content_node].set_packet("www.google.com/logo2.png")
  # want_content_node = 92
  # nodes[want_content_node].set_packet("www.google.com/logo.png")
  # want_content_node = 50
  # nodes[want_content_node].set_packet("www.google.com/logo.png")
  # want_content_node = 70
  # nodes[want_content_node].set_packet("www.google.com/logo.png")
  if protocol == "slime":
    want_content_node = 93
    nodes[want_content_node].set_packet("www.google.com/logo.png")  # コンテンツの位置を知らない

  file_name = get_file_name(nodes)
  print(file_name)
  fig = plt.figure(figsize=(10, 10))

  trafic_list = []

  def animate(i):
    # if i == 50:
    #   want_content_node = 47
    #   nodes[want_content_node].set_packet("www.google.com/logo.png")
    #   want_content_node = 71
    #   nodes[want_content_node].set_packet("www.google.com/logo.png")

    plt.cla()
    nodes_position = get_nodes_position(nodes)
    nodes_link = get_nodes_link(nodes)
    nodes_color = get_nodes_color(nodes)
    nodes_name = get_nodes_name(nodes)
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(nodes_link)

    if protocol == "pbr" and i == 20:
      want_content_node = 93
      nodes[want_content_node].set_packet("www.google.com/logo.png")  # コンテンツの位置を知らない

      # if loop_count == 0: # コンテンツが全て到着時，再びコンテンツを要求
      #   nodes[want_content_node].set_packet("www.google.com/logo.png", nodes[have_content_node].position)
      #   loop_count = node.que.qsize()

    if protocol == "slime":
      for _node in nodes:
        if not _node.f_pit:
          continue
        for k, vs in _node.f_pit.items():
          for v in vs:
            print("Node{} → Node{}".format(_node.number, v.number), end=",")
        print("")

    que = queue.Queue()
    for _node in nodes:
      if not _node.buffer_queue.qsize():
        continue
      que.put(_node)
    print("Process Node : {}".format(que.qsize()))
    edges_communication = []
    trafic_num = 0
    while not que.empty():
      _node = que.get()
      print("Node{} process packet-protocol".format(_node.number))
      _node.packet_protocol(nodes, time=i)
      trafic_num += 1
      # trafic_num += len(_node.select_next_node)
      for n in _node.select_next_node:
        print("Node{} → Node{}".format(_node.number, n.number))
        from_node, to_node = _node, n
        type_packet = _node.packet_type
        if from_node.number > to_node.number:
          from_node, to_node = to_node, from_node
        edges_communication.append((from_node, to_node, type_packet))

    trafic_list.append(trafic_num)

    edges_color = get_eges_color(nodes_link, edges_communication)

    nx.draw_networkx_nodes(G, nodes_position, node_size=400, alpha=1, node_color=nodes_color)
    nx.draw_networkx_edges(G, nodes_position, label=1, edge_color=edges_color, width=2)
    nx.draw_networkx_labels(G, nodes_position, nodes_name, font_size=10, font_color="white")
    plt.axis('off')
    plt.title("t=" + str(i))

    # グラフの保存
    plt.savefig("Export/netork.png")
    # グラフの表示
    # plt.pause(0.001)
    # nodes_move(nodes)
    return

  anim = FuncAnimation(fig, animate, frames=t, interval=10, repeat=True)
  anim.save("Export/{}_{}.gif".format(protocol, file_name), writer="imagemagick", fps=fps)
  # create_graph(name="traffic", x=trafic_list, y=list(range(len(trafic_list))))
  for _node in nodes:
    if not _node.request_content:
      continue
    print("Node{}".format(_node.number), end=" ")
    for k, v in _node.request_content.items():
      print("Content_id:{} Delivery rate:{}".format(k, v), end=" ")
    for k, v in _node.get_content_time.items():
      print("end to end time :{}".format(v))
  return


if __name__ == "__main__":
  fps = 30
  t = 100
  random.seed(6)
  main("slime")
