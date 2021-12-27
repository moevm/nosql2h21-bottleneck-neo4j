from flask import Flask, request
from flask_cors import CORS
import json
from bottleNeckFinder import BottleneckFinder

app = Flask(__name__)
CORS(app)
bottleNeckFinder = BottleneckFinder()

@app.route('/import', methods=['POST'])
async def importByPolygon():
    try:
        data = json.loads(request.get_data())
        points = []
        if(data):
            points = ["%f %f" % tuple(point) for point in data]

        bottleNeckFinder.graduateLines(points)
        return "Success", 200
    except Exception as e:
        print(e)
        return "", 400

@app.route('/polygon', methods=['POST'])
async def getByPolygon():
    try:
        data = json.loads(request.get_data())
        points = []
        if(data):
            points = ["%f %f" % tuple(point) for point in data]

        result = bottleNeckFinder.getVerdict(points)
        return json.dumps(result, ensure_ascii=False), 200
    except Exception as e:
        print(e)
        return "", 400

if __name__ == "__main__":
    bottleNeckFinder.connectDB("bolt://database:7687", "neo4j", "123")
    app.run(host="0.0.0.0", port=5000, debug=True)