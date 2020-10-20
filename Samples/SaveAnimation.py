# matplotlibで描画したグラフをgif or mp4で保存するプログラム
'''
参考文献:
[Pythonでリアルタイムにグラフを描画する方法を現役エンジニアが解説【初心者向け】](https://techacademy.jp/magazine/34049)
'''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def f(x):
  return -(x - 3)**3 + 2 * (x - 3)


def main():
  fig, ax = plt.subplots()

  # 玉の初期値
  my_dot, = plt.plot([0], [f(0)], 'ro')
  # 玉が動く関数

  def update_ani(i):
    my_dot.set_data(i, f(i))
    return my_dot,

  # 玉が動くアニメーション
  ani = animation.FuncAnimation(fig,
                                update_ani,
                                frames=t,
                                interval=10,
                                blit=True,
                                repeat=False)

  # 動画ファイルで保存
  if flag_mp4:
    ani.save('./Export/SaveAnimation.mp4', writer='ffmpeg', fps=my_fps)
  else:
    ani.save("./Export/SaveAnimaiton.gif", writer="imagemagick", fps=my_fps)

  # plt.show()


if __name__ == '__main__':
  xy_range = [0, 6, -10, 10]
  x = np.arange(0, 6, 0.001)  # 道のx範囲（関数のx軸の範囲）
  t = np.arange(0, 6, 0.1)  # 玉が動くxの範囲

  flag_mp4 = False  # mp4で保存しない場合はFalse
  my_fps = 30  # Frames Per Second

  main()
