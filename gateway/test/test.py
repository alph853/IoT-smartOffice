brightness = 20
color = ((100, 100, 100), "blue", (100, 100, 100), (100, 100, 100))

COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
}

data = tuple(map(lambda x: tuple(map(lambda y: int(y * brightness / 100),
             x if type(x) is not str else COLOR_MAP[x])), color))

print(data)
