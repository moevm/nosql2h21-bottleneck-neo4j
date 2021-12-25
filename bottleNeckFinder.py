import json

def graduateLines(rawGraph):
    with open("graph.json", "w", encoding="utf-") as file:
        json.dump(rawGraph, file, indent=4, ensure_ascii=False)

    lines = []
    for line in rawGraph["features"]:
        lines.append({"points": line["geometry"]["coordinates"], "load": 0.0})
    return lines