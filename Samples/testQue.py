# !/Users/tsubasatakaoka/Desktop/CONwithPhS/.venv/bin/python
# -*- coding: utf-8 -*-
import queue
import random


class test:
  def __init__(self, a):
    self.a = a
    self.b = 1

  def hoge(self):
    print("hoge" + str(self.a + 1))
    if self.a == 3:
      self.a += 10
      q.put(self)
    return

  def huga(self):
    print("huga" + str(self.a + 10))
    return


# LIFOキューの作成
q = queue.Queue()
tests = []
# キューにデータを挿入する。挿入するデータは「0, 1, 2, 3, 4」
for i in range(5):
  tests.append(test(i))

# キューにhogeの順番を格納
for t in tests:
  if random.randint(0, 1) == 1:
    q.put((t, "huga"))
  else:
    q.put((t, "hoge"))


# キューからデータがなくなるまで取り出しを行う
while not q.empty():
  print(q.qsize())
  _q = q.get()
  if _q[1] == "hoge":
    _q[0].hoge()
  else:
    _q[0].huga()
