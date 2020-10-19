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

MAX_NODES = 100


def main():
  G = nx.Graph()
  nodes = [node()] * MAX_NODES
  G.add_nodes_from(nodes)

  print("Hello World!")


if __name__ == "__main__":
  main()
