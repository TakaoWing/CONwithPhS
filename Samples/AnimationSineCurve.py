import matplotlib.pyplot as plt
import numpy as np

# 描画領域を取得
fig, ax = plt.subplots(1, 1)

# y軸方向の描画幅を指定
ax.set_ylim((-1.1, 1.1))

# x軸:時刻
x = np.arange(0, 100, 0.5)

# 周波数を高くしていく
for Hz in np.arange(0.1, 10.1, 0.01):
  # sin波を取得
  y = np.sin(2.0 * np.pi * (x * Hz) / 100)
  # グラフを描画する
  line, = ax.plot(x, y, color='blue')
  # 次の描画まで0.01秒待つ
  plt.pause(0.01)
  # グラフをクリア
  line.remove()