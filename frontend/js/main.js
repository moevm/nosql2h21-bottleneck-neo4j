ymaps.ready(['ext.paintOnMap']).then(function () {
    var map = new ymaps.Map('map', {
        center: [55.75, 37.62],
        zoom: 14,
        controls: ["zoomControl"]
    });

    var paintProcess;

    // Опции многоугольника или линии.
    var styles = {strokeColor: '#00ff00', strokeOpacity: 0.5, strokeWidth: 3, fillColor: '#00ff00', fillOpacity: 0.2};

    var currentIndex = 0;

    // Подпишемся на событие нажатия кнопки мыши.
    map.events.add('mousedown', function (e) {
        // Если кнопка мыши была нажата с зажатой клавишей "alt", то начинаем рисование контура.
        if (e.get('altKey')) {
            if (currentIndex == styles.length - 1) {
                currentIndex = 0;
            } else {
                currentIndex += 1;
            }
            paintProcess = ymaps.ext.paintOnMap(map, e, {style: styles[currentIndex]});
        }
    });

    // Подпишемся на событие отпускания кнопки мыши.
    map.events.add('mouseup', function (e) {
        if (paintProcess) {

            // Получаем координаты отрисованного контура.
            var coordinates = paintProcess.finishPaintingAt(e);
            paintProcess = null;
            // В зависимости от состояния кнопки добавляем на карту многоугольник или линию с полученными координатами.
            var geoObject = new ymaps.Polygon([coordinates], {}, styles[currentIndex]);

            map.geoObjects.add(geoObject);
        }
    });

    var button = new ymaps.control.Button({data: {content: 'Пробки'}, options: {maxWidth: 150}});
    map.controls.add(button);

    var button = new ymaps.control.Button({data: {content: 'Узкие места'}, options: {maxWidth: 150}});
    map.controls.add(button);

}).catch(console.error);