import overpass
from neo4jProvider import Neo4jProvider
from datetime import datetime
provider = Neo4jProvider("bolt://localhost:7687", "neo4j", "123")
api = overpass.API(endpoint="https://overpass.kumi.systems/api/interpreter")

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
    lines = []

    for node in rawGraph["elements"]:
        try:
            if node["type"] == "node":
                provider.writePoint(node)
            elif node["type"] == "way":
                lines.append(provider.writeLine(node))
        except:
            continue

    provider.updateLoad()
    print("%s consumed to write %d lines" % (datetime.now() - start_time, len(lines)))

    return lines
    
def writeLines(nodeIds):
    mapRequest = '(\
                way(id:%s);\
                node(w);\
               );'
    rawGraph = api.get(mapRequest % ", ".join(nodeIds), verbosity='tags body',
                           responseformat="json")
    
    return writeRawGraph(rawGraph)
    
def getGraduation(rawGraph):
    lines = []
    linestoWrite = []

    start_time = datetime.now()

    for node in rawGraph["elements"]:
        if not provider.haveLine(node):
            linestoWrite.append(str(node["id"]))


    if len(linestoWrite) > 0:
        writeLines(linestoWrite)

    start_time = datetime.now()

    for node in rawGraph["elements"]:
        lines.append(provider.getLine(node))

    print("%s consumed to read %d lines" % (datetime.now() - start_time, len(lines)))
    
    return lines