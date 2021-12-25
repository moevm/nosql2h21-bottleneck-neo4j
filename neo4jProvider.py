from typing import Dict, List
from neo4j import GraphDatabase

class Neo4jProvider():
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def __del__(self):
        self.driver.close()

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
            
            return session.write_transaction(self.__createLine, id, lanes, maxSpeed, line["nodes"])



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
        points = []
        
        for pointId in nodes:
            points.append(list(Neo4jProvider.__addRelation(context, id, pointId)))
        
        return points
            
    @staticmethod
    def __addRelation(context, lineId: int, pointId: int):
        result = context.run("MATCH (point:Point {id: $pointId}), "
                             "      (line:Line {id: $lineId}) "
                             "MERGE (point)-[:included]->(line) "
                             "MERGE (line)-[:contains]->(point) "
                             "RETURN point.lat, point.lot",
                             pointId=pointId, lineId=lineId)
        return result.single()

def writeRawGraph(provider, rawGraph):
    lines = []

    for node in rawGraph["elements"]:
            try:
                if node["type"] == "node":
                    provider.writePoint(node)
                elif node["type"] == "way":
                    lines.append(provider.writeLine(node))
            except:
                continue
    
    return lines
