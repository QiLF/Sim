MAX = 0x00ff00
for i in range(15):
    offset = 8*i
    print('"#', end="")
    print(hex(MAX+offset+(offset<<16)), end='",')
