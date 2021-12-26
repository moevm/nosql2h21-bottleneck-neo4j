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
    
    def haveLine(self, line):
        with self.driver.session() as session:
            id = line["id"]

            return session.write_transaction(self.__haveLine, id)
    
    @staticmethod
    def __haveLine(context, id:int):
        result = context.run("MATCH (line:Line {id:$id})"
                              "RETURN line.id", id=id)

        if len(result.single()) > 0:
            return True
        else:
            return False

    def updateLoad(self):
        with self.driver.session() as session:
            session.write_transaction(self.__updateLoad)

    @staticmethod
    def __updateLoad(context):
        context.run("match (l:Line) "
                    "set l.load = $basicLoad", basicLoad=0)

        context.run("match (l:Line)-[:contains]->(p:Point) "
                    "where p.isTrafficSignal = true "
                    "set l.load = l.load + $weight", weight=0.1)
        
        context.run("match (l1:Line)-[:contains]->(p:Point) "
                    "match (p)-[:included]->(l2:Line) "
                    "where l1.id <> l2.id and l1.lanes > l2.lanes "
                    "set l1.load = l1.load + $weight", weight=0.4)

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
        results = context.run("MATCH (line:Line {id:$id})-[rel:contains]->(point:Point)"
                              "RETURN rel.number, line.load, point.lat, point.lon", id=id)
        points = []
        load = 0
        for point in sorted(list(results)):
            points.append(list(point[2::]))
            load = point[1]

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
        
        number = 0
        for pointId in nodes:
            points.append(list(Neo4jProvider.__addRelation(context, id, pointId, number)))
            number += 1
        
        return {"points": points, "load": result.single()}
            
    @staticmethod
    def __addRelation(context, lineId: int, pointId: int, number: int):
        result = context.run("MATCH (point:Point {id: $pointId}), "
                             "      (line:Line {id: $lineId}) "
                             "MERGE (point)-[:included]->(line) "
                             "MERGE (line)-[:contains {number:$number}]->(point) "
                             "RETURN point.lat, point.lon",
                             pointId=pointId, lineId=lineId, number=number)

        return result.single()
    