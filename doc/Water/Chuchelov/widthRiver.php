<?php

# Код нахождение рек и ширины рек между 2мя юнитами
# Input: Координаты юнитов в json формате; {{'x_unit1', 'y_unit1'}, {'x_unit2', 'y_unit2'}}
# Output: json строка типа: {'name_river': {'id':10222, 'width': 200, 'x_cross1':51.05, 'y_cross1':21.05, 'x_cross2': 52.05, 'y_cross2': 22.05 }} Если река без ширины,
# возвращает -1 в значении ширины

function getWidthRiver($coordinates) {

    $units = json_decode($coordinates);

    $unit_1 = $units[0][0] . ',' . $units[0][1];
    $unit_2 = $units[1][0] . ',' . $units[1][1];

    if (file_exists('poland.sqlite')) {
        $db = new SQLite3("poland.sqlite");
    }
    if (file_exists('mod_spatialite.so.7.1.0')) {
        $db->loadExtension('mod_spatialite.so.7.1.0');
    }

    $db->exec("SELECT InitSpatialMetadata()");

    # Запрос на поиск пересечения линии между юнитами и рек.
    # Переменная out выходной словарь с данными

    $rs = $db->query("SELECT id, name, sub_type, AsGeoJSON(Geometry) AS json FROM ln_waterway WHERE Crosses(MakeLine(MakePoint($unit_1), MakePoint($unit_2)), Geometry)");

    # Если тип найденной реки "riverbank", для нее находим ширину реки. Иначе width = -1;
    # В выдачу добавлены точки пересечения прямой между юнитами с рекой, т.е. по сути точки берега реки, через который,
    # проходит бой юнитов.
    # В переменной $row[0] находятся точки персечения

    while ($river = $rs->fetchArray()) {
        if ($river['sub_type'] == 'riverbank') {
            $points = $db->query("SELECT AsGeoJSON(Intersection(MakeLine(MakePoint(". $unit_1 ."), MakePoint(". $unit_2 .")), GeomFromGeoJSON('" . $river['json'] . "')))");
            $row = $points->fetchArray();
            $jdecode = json_decode($row[0]);
            $i = 0;
            foreach ($jdecode->coordinates as $value) {
                $lng[$i] = $value[0];
                $lat[$i] = $value[1];
                $i++;
            }
            $width = widthRiver($lat[0], $lng[0], $lat[1], $lng[1]);
            $out[$river['name']] = ['id' => $river['id'],
                'width' => $width,
                'x_cross1' => $lng[0],
                'y_cross1' => $lat[0],
                'x_cross2' => $lng[1],
                'y_cross2' => $lat[1]];
        } else {
            if (!$out[$river['name']]) {
                $out[$river['name']] = ['id' => $river['id'],
                    'width' => -1];
            }
        }
    }

    $jencode = json_encode($out);

    return $jencode;
}

# Функция расчета ширины реки
function widthRiver($lat1, $lng1, $lat2, $lng2) {

#Coordinates to radian
    $pi = 3.14;
    $EARTH_RADIUS = 6372795;
    $rLat1 = $lat1 * $pi /180;
    $rLat2 = $lat2 * $pi /180;
    $rLng1 = $lng1 * $pi /180;
    $rLng2 = $lng2 * $pi /180;

#Cosinus and sinus coordinates
    $cLat1 = cos($rLat1);
    $cLat2 = cos($rLat2);
    $sLan1 = sin($rLat1);
    $sLan2 = sin($rLat2);
    $deltaLng = $rLng2 - $rLng1;
    $cDelta = cos($deltaLng);
    $sDelta = sin($deltaLng);

#length from coordinates

    $x = sqrt(pow($cLat2 * $sDelta, 2) + pow($cLat1 * $sLan2 - $sLan1 * $cLat2 * $cDelta,2));
    $y = ($sLan1 * $sLan2 + $cLat1 * $cLat2 * $cDelta);

    $width = atan($x / $y) * $EARTH_RADIUS;

    return $width;
}

#Test
$arr = json_encode([[20.931325,52.268881], [21.023444,52.498865]]);
$test = getWidthRiver($arr);
echo $test;