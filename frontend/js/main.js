ymaps.ready(['ext.paintOnMap']).then(function () {
    var map = new ymaps.Map('map', {
        center: [55.75, 37.62],
        zoom: 14,
        controls: ["zoomControl", 'trafficControl']
    });

    var paintProcess;

    // Опции многоугольника или линии.
    var styles = {strokeColor: '#0000ff', strokeOpacity: 0.5, strokeWidth: 3, fillColor: '#0000ff', fillOpacity: 0.2};

    map.events.add('mousedown', function (e) {
        // Если кнопка мыши была нажата с зажатой клавишей "alt", то начинаем рисование контура.
        if (e.get('altKey')) {
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
            })
        }
    });

}).catch(console.error);