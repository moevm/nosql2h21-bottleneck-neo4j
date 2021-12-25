import json
import random

def graduateLines(rawGraph):
    with open("graph.json", "w", encoding="utf-8") as file:
        json.dump(rawGraph, file, indent=4, ensure_ascii=False)

    lines = []
    for line in rawGraph["features"]:
        points = [list(reversed(coord)) for coord in line["geometry"]["coordinates"]]
        lines.append({"points": points, "load": random.random()})
    return lines