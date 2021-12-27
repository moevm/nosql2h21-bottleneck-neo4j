import overpass
from neo4jProvider import Neo4jProvider
from datetime import datetime
api = overpass.API(endpoint="https://overpass.kumi.systems/api/interpreter")

class BottleneckFinder:
    def connectDB(self, url, username, password):
        self.provider = Neo4jProvider(url, username, password)

    def graduateLines(self, points):
        mapRequest = '(\
                    way\
                    (poly: "%(poly)s")\
                    ["highway"~"primary|secondary|residential|tertiary|unclassified"];\
                    node(w);\
                );'
        rawGraph = api.get(mapRequest % {"poly": (" ").join(points)}, verbosity='tags body',
                            responseformat="json")

        self.writeRawGraph(rawGraph)


    def getVerdict(self, points):
        mapRequest = '(\
                    way\
                    (poly: "%(poly)s")\
                    ["highway"~"primary|secondary|residential|tertiary|unclassified"];\
                );'
        rawGraph = api.get(mapRequest % {"poly": (" ").join(points)}, verbosity='ids',
                            responseformat="json")

        result = self.getGraduation(rawGraph)
        if result:
            return result

    def writeRawGraph(self, rawGraph):
        start_time = datetime.now()
        lines = []

        for node in rawGraph["elements"]:
            try:
                if node["type"] == "node":
                    self.provider.writePoint(node)
                elif node["type"] == "way":
                    lines.append(self.provider.writeLine(node))
            except:
                continue

        self.provider.updateLoad()
        print("%s consumed to write %d lines" % (datetime.now() - start_time, len(lines)))

        return lines
        
    def writeLines(self, nodeIds):
        mapRequest = '(\
                    way(id:%s);\
                    node(w);\
                );'
        rawGraph = api.get(mapRequest % ", ".join(nodeIds), verbosity='tags body',
                            responseformat="json")
        
        return self.writeRawGraph(rawGraph)
        
    def getGraduation(self, rawGraph):
        lines = []
        linestoWrite = []

        start_time = datetime.now()

        for node in rawGraph["elements"]:
            if not self.provider.haveLine(node):
                linestoWrite.append(str(node["id"]))


        if len(linestoWrite) > 0:
            self.writeLines(linestoWrite)

        start_time = datetime.now()

        for node in rawGraph["elements"]:
            lines.append(self.provider.getLine(node))

        print("%s consumed to read %d lines" % (datetime.now() - start_time, len(lines)))
        
        return lines