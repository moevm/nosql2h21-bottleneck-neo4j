import random
from neo4jProvider import Neo4jProvider, writeRawGraph

provider = Neo4jProvider("bolt://localhost:7687", "neo4j", "123")

def graduateLines(rawGraph):
    lines = [{"points": line, "load": random.random()} 
             for line in writeRawGraph(provider,rawGraph)]

    return lines

def getVerdict(rawGraph):
    return graduateLines(rawGraph)