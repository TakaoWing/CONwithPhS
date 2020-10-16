# numpy と　matplotlibが正常にインストールされているか確認するプログラム
'''
参考文献:
[Windows + Python + PipEnv + Visual Studio Code でPython開発環境](https://qiita.com/youkidkk/items/b674e6ace96eb227cc28)
'''
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-np.pi, np.pi)
y = np.sin(x)
plt.plot(x, y)
plt.show()
