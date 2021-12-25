ymaps.ready(['ext.paintOnMap']).then(function () {
    var map = new ymaps.Map('map', {
        center: [55.75, 37.62],
        zoom: 14,
        controls: ["zoomControl", 'trafficControl', 'geolocationControl', "searchControl"]
    });

    var paintProcess;
    var styles = {strokeColor: '#0000ff', strokeOpacity: 0.5, strokeWidth: 3, fillColor: '#0000ff', fillOpacity: 0.2};
    var button = new ymaps.control.Button({data: {content: 'Режим выделеия'}, options: {maxWidth: 150}});
    map.controls.add(button);

    map.events.add('mousedown', function (e) {
        if (e.get('altKey') || button.isSelected()) {
            paintProcess = ymaps.ext.paintOnMap(map, e, {style: styles});
        }
    });
    var lastGeoObject;
    // Подпишемся на событие отпускания кнопки мыши.
    map.events.add('mouseup', function (e) {
        if (paintProcess) {

            // Получаем координаты отрисованного контура.
            var coordinates = paintProcess.finishPaintingAt(e);
            paintProcess = null;
            var geoObject = new ymaps.Polygon([coordinates], {}, styles);
            var COORD = [];
            for(var i = 0; i < coordinates.length; i++){
                COORD[i] = [
                    coordinates[i][0],
                    coordinates[i][1]
                ]
            }
            var JSON_COORDS = JSON.stringify(COORD);
            map.geoObjects.removeAll();
            map.geoObjects.add(geoObject);
            GetBottlenecks(JSON_COORDS, function(Response){
                console.log(Response.responseText);
                var json = JSON.parse(Response.responseText);
                for(var i = 0; i < json.length; i++){
                    console.log(JSON.stringify(json[i]["points"]));
                    var polyline = new ymaps.Polyline(json[i]["points"], {}, {
                        strokeWidth: 5,
                        strokeColor: perc2color(100 - (json[i]["load"] * 100)),
                        opacity: 0.5
                    });
                    map.geoObjects.add(polyline);
                }
            })
        }
    });

}).catch(console.error);


function perc2color(perc) {
    var r, g, b = 0;
    if(perc < 50) {
        r = 255;
        g = Math.round(5.1 * perc);
    }
    else {
        g = 255;
        r = Math.round(510 - 5.10 * perc);
    }
    var h = r * 0x10000 + g * 0x100 + b * 0x1;
    return '#' + ('000000' + h.toString(16)).slice(-6);
}