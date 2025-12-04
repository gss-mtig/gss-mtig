# 🚆 Posicionamiento de trenes FGC – Tiempo real

## API de FGC – Datos en tiempo real

La API que usaremos:
https://dadesobertes.fgc.cat/explore/dataset/posicionament-dels-trens/api/

Para ver la URL de la llama que devuelva un GeoJSON consultamos https://dadesobertes.fgc.cat/api/explore/v2.1/console

Ponemos:
* `dataset_id` = posicionament-dels-trens
* `format` = geojson

Presionamos el boton de `execute` y vemos la respuesta.

## API de FGC – Líneas de la red de FGC

Abrimos una nueva pestaña en el navegador.

La API que usaremos:
https://dadesobertes.fgc.cat/explore/dataset/lineas-red-fgc/api/

Para ver la URL de la llama que devuelva un JSON consultamos https://dadesobertes.fgc.cat/api/explore/v2.1/console

Ponemos:
* `dataset_id` = lineas-red-fgc
* `format` = json

Presionamos el boton de `execute` y vemos la respuesta.

## Mapa de trenes en tiempo real

- Crear una carpeta con el nombre de *fgc-realtime*.
- Crear un archivo con el nombre de *index.html* dentro de la carpeta.
- Abrir el archivo index.html con un editor de texto y copiar el siguiente código.

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Mapa FGC en tiempo real</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <style>
    #map {
      height: 100%;
      width: 100%;
      position: absolute;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    var map = L.map('map');

    map.setView([41.3869, 2.1701], 10);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  </script>
</body>
</html>
```

- Abrir el archivo index.html en el navegador para confirmar que se carga un mapa centrado en Barcelona.

- Agregar el plugin para cargar datos en tiempo real. Para ellos utilizaremos el plugin Leaflet Realtime [^3].  Copiar lo siguiente justo después de cuando carguemos la librería de Leaflet.

```html hl_lines="10"
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Mapa FGC en tiempo real</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <style>
    #map {
      height: 100%;
      width: 100%;
      position: absolute;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    var map = L.map('map');

    map.setView([41.3869, 2.1701], 10);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  </script>
</body>
</html>
```

- Crear una funcion para cargar la informacion de los trenes

```html hl_lines="31-42"
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Mapa FGC en tiempo real</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <style>
    #map {
      height: 100%;
      width: 100%;
      position: absolute;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    var map = L.map('map');

    map.setView([41.3869, 2.1701], 10);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    async function cargarTrenes() {
      const trenesURL = "URL TRENES TIEMPO REAL";
     
      const trenes = L.realtime(trenesURL, {
        interval: 2 * 1000,
        pointToLayer: function(geoJsonPoint, latlng) {
          return L.circleMarker(latlng);
        }
      }).addTo(map);
    }

    cargarTrenes();
  </script>
</body>
</html>
```
  
- Cambiar `URL TRENES TIEMPO REAL` por la URL obtenida en **API de FGC – Datos en tiempo real**

## Pintar los trenes segun el color de la linea

- Crear la variable donde se va a guardar la informacion de las lineas y agregar la URL donde obtener la info de las lineas

```html hl_lines="31 35"
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Mapa FGC en tiempo real</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <style>
    #map {
      height: 100%;
      width: 100%;
      position: absolute;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    var map = L.map('map');

    map.setView([41.3869, 2.1701], 10);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let lineasInfo;

    async function cargarTrenes() {
      const trenesURL = "URL TRENES TIEMPO REAL";
      const lineasURL = "URL INFO LINEAS";

      const trenes = L.realtime(trenesURL, {
        interval: 2 * 1000,
        pointToLayer: function(geoJsonPoint, latlng) {
          return L.circleMarker(latlng);
        }
      }).addTo(map);
    }

    cargarTrenes();
  </script>
</body>
</html>
```

- Cambiar `URL INFO LINEAS` por la URL obtenida en **API de FGC – Líneas de la red de FGC**

- Cargar la informacion de las lineas

```html hl_lines="37-38"
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Mapa FGC en tiempo real</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <style>
    #map {
      height: 100%;
      width: 100%;
      position: absolute;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    var map = L.map('map');

    map.setView([41.3869, 2.1701], 10);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let lineasInfo;

    async function cargarTrenes() {
      const trenesURL = "URL TRENES TIEMPO REAL";
      const lineasURL = "URL INFO LINEAS";

      const resp = await fetch(lineasURL);
      lineasInfo = await resp.json();

      const trenes = L.realtime(trenesURL, {
        interval: 2 * 1000,
        pointToLayer: function(geoJsonPoint, latlng) {
          return L.circleMarker(latlng);
        }
      }).addTo(map);
    }

    cargarTrenes();
  </script>
</body>
</html>
```

- Agregar estilo a la capa de los trenes

```html hl_lines="44-51"
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Mapa FGC en tiempo real</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <style>
    #map {
      height: 100%;
      width: 100%;
      position: absolute;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    var map = L.map('map');

    map.setView([41.3869, 2.1701], 10);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let lineasInfo;

    async function cargarTrenes() {
      const trenesURL = "URL TRENES TIEMPO REAL";
      const lineasURL = "URL INFO LINEAS";

      const resp = await fetch(lineasURL);
      lineasInfo = await resp.json();

      const trenes = L.realtime(trenesURL, {
        interval: 2 * 1000,
        pointToLayer: function(geoJsonPoint, latlng) {
          return L.circleMarker(latlng);
        },
        style: function (feature) {
          return {
            color: "#FF0000",
            fillColor: "#0000FF",
            fillOpacity: 0.5
          };
        }
      }).addTo(map);
    }

    cargarTrenes();
  </script>
</body>
</html>
```

- Crear una funcion para que retorne el color de la linea segun los datos del FGC

```html hl_lines="55-67"
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Mapa FGC en tiempo real</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <style>
    #map {
      height: 100%;
      width: 100%;
      position: absolute;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    var map = L.map('map');

    map.setView([41.3869, 2.1701], 10);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let lineasInfo;

    async function cargarTrenes() {
      const trenesURL = "URL TRENES TIEMPO REAL";
      const lineasURL = "URL INFO LINEAS";

      const resp = await fetch(lineasURL);
      lineasInfo = await resp.json();

      const trenes = L.realtime(trenesURL, {
        interval: 2 * 1000,
        pointToLayer: function(geoJsonPoint, latlng) {
          return L.circleMarker(latlng);
        },
        style: function (feature) {
          return {
            color: "#FF0000",
            fillColor: "#0000FF",
            fillOpacity: 0.5
          };
        }
      }).addTo(map);
    }

    function getColorLinea(idLinea) {
      const rutas = lineasInfo;

      const ruta = rutas.find(r => 
        r.route_id.toUpperCase() === idLinea.toUpperCase()
      );

      if (!ruta) {
        return "#000000"; // color por defecto
      }

      return "#" + ruta.route_color;
    }

    cargarTrenes();
  </script>
</body>
</html>
```

- Usar la funcion `getColorLinea` para establecer el color de los puntos

```html hl_lines="47-48"
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Mapa FGC en tiempo real</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <style>
    #map {
      height: 100%;
      width: 100%;
      position: absolute;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    var map = L.map('map');

    map.setView([41.3869, 2.1701], 10);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let lineasInfo;

    async function cargarTrenes() {
      const trenesURL = "URL TRENES TIEMPO REAL";
      const lineasURL = "URL INFO LINEAS";

      const resp = await fetch(lineasURL);
      lineasInfo = await resp.json();

      const trenes = L.realtime(trenesURL, {
        interval: 2 * 1000,
        pointToLayer: function(geoJsonPoint, latlng) {
          return L.circleMarker(latlng);
        },
        style: function (feature) {
          return {
            color: getColorLinea(feature.properties.lin),
            fillColor: getColorLinea(feature.properties.lin),
            fillOpacity: 0.5
          };
        }
      }).addTo(map);
    }

    function getColorLinea(idLinea) {
      const rutas = lineasInfo;

      const ruta = rutas.find(r => 
        r.route_id.toUpperCase() === idLinea.toUpperCase()
      );

      if (!ruta) {
        return "#000000"; // color por defecto
      }

      return "#" + ruta.route_color;
    }

    cargarTrenes();
  </script>
</body>
</html>
```


## Referencias

[^3]: https://github.com/perliedman/leaflet-realtime
