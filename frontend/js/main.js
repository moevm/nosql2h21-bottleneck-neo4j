ymaps.ready(['ext.paintOnMap']).then(function () {
    var map = new ymaps.Map('map', {
        center: [55.75, 37.62],
        zoom: 14,
        controls: ["zoomControl"]
    });

    var paintProcess;

    // Опции многоугольника или линии.
    var styles = {strokeColor: '#0000ff', strokeOpacity: 0.5, strokeWidth: 3, fillColor: '#0000ff', fillOpacity: 0.2};

    var currentIndex = 0;

    var traffic_jams = new ymaps.control.Button({data: {content: 'Пробки'}, options: {maxWidth: 150}});
    map.controls.add(traffic_jams);

    var button = new ymaps.control.Button({data: {content: 'Узкие места'}, options: {maxWidth: 150}});
    map.controls.add(button);


    // Подпишемся на событие нажатия кнопки мыши.
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
            GetBottlenecks(JSON_COORDS, function(Response){
                console.log(Response);
            })
            map.geoObjects.removeAll();
            map.geoObjects.add(geoObject);
        }
    });

}).catch(console.error);