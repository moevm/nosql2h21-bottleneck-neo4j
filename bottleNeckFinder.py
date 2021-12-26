import overpass
from neo4jProvider import Neo4jProvider, writeRawGraph, getGraduation
from datetime import datetime

provider = Neo4jProvider("bolt://localhost:7687", "neo4j", "123")
api = overpass.API()

def graduateLines(points):
    mapRequest = '(\
                way\
                (poly: "%(poly)s")\
                ["highway"~"primary|secondary|residential|tertiary|unclassified"];\
                node(w);\
               );'
    rawGraph = api.get(mapRequest % {"poly": (" ").join(points)}, verbosity='tags body',
                           responseformat="json")

    writeRawGraph(rawGraph)


def getVerdict(points):
    mapRequest = '(\
                way\
                (poly: "%(poly)s")\
                ["highway"~"primary|secondary|residential|tertiary|unclassified"];\
               );'
    rawGraph = api.get(mapRequest % {"poly": (" ").join(points)}, verbosity='ids',
                           responseformat="json")

    result = getGraduation(rawGraph)
    if result:
        return result

def writeRawGraph(rawGraph):
    start_time = datetime.now()

    for node in rawGraph["elements"]:
            try:
                if node["type"] == "node":
                    provider.writePoint(node)
                elif node["type"] == "way":
                    provider.writeLine(node)
            except:
                continue

    print("%s consumed to write %d nodes" % (datetime.now() - start_time, len(rawGraph["elements"])))
    
def writeLine(nodeId):
    mapRequest = '(\
                way(id:%d)\
                node(w);\
               );'
    rawGraph = api.get(mapRequest % nodeId, verbosity='tags body',
                           responseformat="json")
    
    for node in rawGraph["elements"]:
            try:
                if node["type"] == "node":
                    provider.writePoint(node)
                elif node["type"] == "way":
                    return provider.writeLine(node)
            except:
                continue
    
def getGraduation(rawGraph):
    lines = []

    start_time = datetime.now()

    for node in rawGraph["elements"]:
            try:
                line = provider.getLine(node)
                if line:
                    lines.append(line)
                else:
                    lines.append(writeLine(line["id"]))
            except:
                continue

    print("%s consumed to read %d nodes" % (datetime.now() - start_time, len(rawGraph["elements"])))
    
    return lines