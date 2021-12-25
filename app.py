import overpass
from flask import Flask, request
import json

app = Flask(__name__)
api = overpass.API()

mapRequest = '(\
                way\
                (poly: "%(poly)s")\
                ["highway"~"primary|residential|tertiary|unclassified"];\
                (\
                    ._;\
                    >;\
                );\
               );'

@app.route('/polygon', methods=['POST'])
def getByPolygon():
    try:
        data = json.loads(request.get_data())
        points = []
        if(data):
            points = ["%f %f" % tuple(point) for point in data]
        
        result = api.get(mapRequest % {"poly": (" ").join(points)})
        return json.dumps(result, ensure_ascii=False), 200
    except Exception:
        return None, 400

if __name__ == "__main__":
    app.run(port=8080, debug=True)