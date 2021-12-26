import random
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

    def getLine(self, line: Dict):
        with self.driver.session() as session:
            id = line["id"]

            return session.write_transaction(self.__getLine, id)

    @staticmethod
    def __getLine(context, id:int):
        results = context.run("MATCH (line:Line {id:$id})-[:contains]->(point:Point)"
                              "RETURN line.load, point.lat, point.lon", id=id)
        points = []
        load = 0
        for point in results:
            points.append(list(point[1::]))
            load = point[0]

        if len(points) > 0:
            return {"points": points, "load": load}
        else:
            return None

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
        result = context.run("MERGE (line:Line {id: $id, lanes: $lanes, maxSpeed: $maxSpeed, load: $load}) "
                             "ON MATCH "
                             "   SET "
                             "       line.lanes=$lanes, "
                             "       line.maxSpeed=$maxSpeed, "
                             "       line.load=$load "
                             "RETURN line.load",
                    id=id, lanes=lanes, maxSpeed=maxSpeed, load=random.random())
        points = []
        
        for pointId in nodes:
            points.append(list(Neo4jProvider.__addRelation(context, id, pointId)))
        
        return {"points": points, "load": result.single()}
            
    @staticmethod
    def __addRelation(context, lineId: int, pointId: int):
        result = context.run("MATCH (point:Point {id: $pointId}), "
                             "      (line:Line {id: $lineId}) "
                             "MERGE (point)-[:included]->(line) "
                             "MERGE (line)-[:contains]->(point) "
                             "RETURN point.lat, point.lon",
                             pointId=pointId, lineId=lineId)

        return result.single()
    