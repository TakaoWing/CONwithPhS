import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()


def plot(data):
  plt.cla()                      # 現在描写されているグラフを消去
  rand = np.random.randn(100)    # 100個の乱数を生成
  plt.axis('off')
  plt.plot(rand)            # グラフを生成


ani = animation.FuncAnimation(fig, plot, interval=100, frames=10)
ani.save("Export/fucanimation.gif", writer="imagemagick")
