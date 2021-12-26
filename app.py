import overpass
from flask import Flask, request
from flask_cors import CORS
import json
import bottleNeckFinder

app = Flask(__name__)
CORS(app)
api = overpass.API()

mapRequest = '(\
                way\
                (poly: "%(poly)s")\
                ["highway"~"primary|secondary|residential|tertiary|unclassified"];\
                node(w);\
               );'

@app.route('/import', methods=['POST'])
def getByPolygon():
    try:
        data = json.loads(request.get_data())
        points = []
        if(data):
            points = ["%f %f" % tuple(point) for point in data]
        
        rawGraph = api.get(mapRequest % {"poly": (" ").join(points)}, verbosity='tags body',
                           responseformat="json")
        return json.dumps(bottleNeckFinder.graduateLines(rawGraph), ensure_ascii=False), 200
    except Exception as e:
        print(e)
        return "", 400

@app.route('/polygon', methods=['POST'])
def getByPolygon():
    try:
        data = json.loads(request.get_data())
        points = []
        if(data):
            points = ["%f %f" % tuple(point) for point in data]
        
        rawGraph = api.get(mapRequest % {"poly": (" ").join(points)}, verbosity='tags body',
                           responseformat="json")
        return json.dumps(bottleNeckFinder.getVerdict(rawGraph), ensure_ascii=False), 200
    except Exception as e:
        print(e)
        return "", 400

if __name__ == "__main__":
    app.run(host="26.101.20.117", port=8080, debug=True)