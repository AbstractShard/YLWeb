from random import shuffle


a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
shuffle(a)

print(a)

b = {
    "a": 1,
    "b": 2,
    "c": 3,
    "d": 4,
    "e": 5
}

b = list(b.items())
shuffle(b)

print(b)