import networkx as nx
import matplotlib.pyplot as plt


def main():
  # グラフを作成する長方形の辺の長さを指定
  n = 10
  m = 10
  node_num = n * m
  # グラフを作る
  G = nx.Graph()

  # 確率0.5でノードを追加
  for i in range(node_num):
    G.add_node(i)
  # ノードから出ているエッジが３つ以上であれば赤色でノードを描画する
  node_color = 'red'

  pos_node = []
  for i in range(n):
    for j in range(m):
      pos_node.append((j, i))
  pos = dict(zip(range(node_num), pos_node))

  nx.draw_networkx_nodes(G, pos, node_size=10,
                         alpha=1, node_color=node_color)

  plt.savefig('./Export/graph_test2.png')


if __name__ == "__main__":
  main()
