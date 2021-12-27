function GetBottlenecks(Polygon, Handler)
{
    SendRequest("POST", "http://127.0.0.1:5000/polygon", Polygon, Handler);
}

function ImportInPolygonData(Polygon, Handler)
{
    SendRequest("POST", "http://127.0.0.1:5000/import", Polygon, Handler);
}