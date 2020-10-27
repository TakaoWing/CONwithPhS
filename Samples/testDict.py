d = {"a": [1], "b": [2], "c": [3]}
d["a"].append(2)
d["aa"] = [10]
print(d)

if "ba" in d:
  if 3 in d["a"]:
    print("あるよ！")
  else:
    print("ないよ！")
    d["a"].append(3)
else:
  print("ないよ!")
  d["ba"] = []
  d["ba"].append(45)

print(d)

d = None
if d is None:
  print("削除されているよ！")
