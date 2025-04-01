a = {1: "hello", 2: {"world": 321}}

def change(me):
  for key, data in a.items():
    if key == 2:
      print("yay")
      a[key]["world"] = 123

print(a)
change(a)
print()
print(a)


