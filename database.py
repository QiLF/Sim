import struct

hash_dictionary = {}
try:
    with open("database/hash", 'rb') as fobj:
        while True:
            key = struct.unpack('i', fobj.read(4))
            value = struct.unpack('i', fobj.read(4))
            hash_dictionary[key] = value
except FileNotFoundError as e:
    print("Sorry, database 'hash' doesn't exist")
except EOFError as e:
    pass
except struct.error:
    pass

value_database = []
try:
    with open("database/value.txt") as fobj:
            value_str = fobj.read()
            value_database = str.split(value_str, '\n')
except FileNotFoundError as e:
    print("Sorry, database 'value.txt' doesn't exist")
remoteness_database = []
try:
    with open("database/remt.txt") as fobj:
        remoteness_str = fobj.read()
        remoteness_database = str.split(remoteness_str, '\n')
        remoteness_database = list(map(int, remoteness_database))
except FileNotFoundError as e:
    print("Sorry, database 'remt.txt' doesn't exist")