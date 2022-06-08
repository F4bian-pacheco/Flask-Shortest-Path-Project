
var datos = get_datos()
console.log(datos)

let port = datos[0]
let url_destino = datos[1]

console.log(port)
console.log(url_destino)

var counter = 0;

const ruta_stops = `http://127.0.0.1:${port}/stops`
const ruta_roads = `http://127.0.0.1:${port}/roads`
var Roads = L.layerGroup().addTo(map);


function onEachFeature(feature, layer) {
    layer.bindPopup(feature.properties.name)
}
$.getJSON(ruta_stops, function (data) {
    var vertex_style = {
        'radius': 5,
        'fillColor': "#ff7800",
        'color': "#000",
        'weight': 1,
        'opacity': 1,
        'fillOpacity': 0.5
    };
    L.geoJSON(data, {
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, vertex_style);
        },
        onEachFeature: onEachFeature
    }).addTo(map).on('click', function (e) {
        if (counter % 2 == 0) {
            document.getElementById('latInput').value = e.latlng.lat;
            document.getElementById('lngInput').value = e.latlng.lng;
        }
        else {
            document.getElementById('latTarget').value = e.latlng.lat;
            document.getElementById('lngTarget').value = e.latlng.lng;
        }
        counter += 1;
    });
});


$("#form").submit(function (e) {
    e.preventDefault();

    $.ajax({
        type: "POST",
        url: url_destino,
        data: $("#form").serialize(),
        success: function (response) {
            Roads.clearLayers();
            var edges_style = {
                'color': '#990000',
                'weight': 3,
                'opacity': 2
            };
            L.geoJSON(response[0], {
                style: edges_style,
            }).addTo(Roads);
            var tiempo = new Number(response[1]);
            $("#tiempo").text(tiempo.toPrecision(8));
        }
    });

});

function limpiar() {
    Roads.clearLayers();
}