from typing import Dict, List
from neo4j import GraphDatabase
import json

class Neo4jProvider():
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def writePoint(self, point: Dict):
        with self.driver.session() as session:
            id = point["id"]
            lat = point["lat"]
            lon = point["lon"]
            isTrafficSignal = False
            try:
                isTrafficSignal = point["tags"]["highway"] == "traffic_signals"
            except:
                pass

            session.write_transaction(self.__createPoint, id, lat, lon, isTrafficSignal)

    def writeLine(self, line: Dict):
        with self.driver.session() as session:
            id = line["id"]
            lanes = 1
            maxSpeed = 60
            try:
                lanes = line["tags"]["lanes"]
                maxSpeed = int(line["tags"]["maxspeed"])
            except:
                pass
            
            session.write_transaction(self.__createLine, id, lanes, maxSpeed, line["nodes"])

    @staticmethod
    def __createPoint(context, id:int, lat: float, lon: float, isTrafficSignal: bool = False):
        context.run("MERGE (point:Point {id: $id, lat: $lat, lon: $lon, isTrafficSignal: $isTrafficSignal}) "
                    "ON MATCH "
                    "   SET "
                    "       point.lat=$lat, "
                    "       point.lon=$lon, "
                    "       point.isTrafficSignal=$isTrafficSignal ",
                    id=id, lat=lat, lon=lon, isTrafficSignal=isTrafficSignal)

    @staticmethod
    def __createLine(context, id:int, lanes: int, maxSpeed: int, nodes: List,):
        context.run("MERGE (line:Line {id: $id, lanes: $lanes, maxSpeed: $maxSpeed}) "
                    "ON MATCH "
                    "   SET "
                    "       line.lanes=$lanes, "
                    "       line.maxSpeed=$maxSpeed ",
                    id=id, lanes=lanes, maxSpeed=maxSpeed)
        
        for pointId in nodes:
            Neo4jProvider.__addRelation(context, id, pointId)
            
    @staticmethod
    def __addRelation(context, lineId: int, pointId: int):
        context.run("MATCH (point:Point {id: $pointId}), "
                    "      (line:Line {id: $lineId}) "
                    "MERGE (point)-[:included]->(line) "
                    "MERGE (line)-[:contains]->(point) ",
                    pointId=pointId, lineId=lineId)

if __name__ == '__main__':
    provider = Neo4jProvider("bolt://localhost:7687", "neo4j", "123")

    with open("graph.json", 'r', encoding='utf-8') as file:
        rawGraph = json.load(file,)
        for node in rawGraph["elements"]:
            try:
                if node["type"] == "node":
                    provider.writePoint(node)
                elif node["type"] == "way":
                    provider.writeLine(node)
            except:
                continue

    provider.close()
