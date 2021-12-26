function GetBottlenecks(Polygon, Handler)
{
    SendRequest("POST", "http://26.101.20.117:8080/polygon", Polygon, Handler);
}