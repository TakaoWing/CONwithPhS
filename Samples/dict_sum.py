d = {'key1': -1, 'key2': -14, 'key3': 47}

total = sum(
    abs(v) for v in d.values()
)

print(total)
