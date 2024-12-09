# Ejemplo servicio bicing Barcelona

## Acceso al servicio de datos del Bicing de Barcelona

En el portal Open data del Ayuntamiento de Barcelona podemos encontrar un dataset (conjunto de datos) que contiene las [estaciones del servicio de Bicing](https://opendata-ajuntament.barcelona.cat/data/es/dataset?q=bicing&sort=fecha_publicacion+desc)

Anteriormente tenían un servicio donde daban toda la información de la estación en tiempo real. Actualmente lo han separado en dos servicios unos con la [información de las estaciones](https://opendata-ajuntament.barcelona.cat/data/es/dataset/informacio-estacions-bicing) (identificador, nombre, coordenadas, etc.) y otro con [estado de las estaciones](https://opendata-ajuntament.barcelona.cat/data/es/dataset/estat-estacions-bicing) (número de bicis disponibles, tipos de bicis, etc)

Si bien el Ayuntamiento de Barcelona no ofrece explícitamente el acceso a los datos del Bicing como un servicio, si que tiene un servicio de datos en tiempo real. La url la podemos encontrar presionando el botón de Descargar del recurso json

![url servicio de bicing](img/bicing.png)
*url servicio de bicing*

!!! info
	  Recientemente han puesto un token para descargar los datos

Al abrir la url https://www.bicing.barcelona/es/get-stations en nuestro navegador observaremos que la respuesta es un archivo json con un conjunto de elementos que tienen las coordenadas de la localización de la estación de bicing, la dirección, la capacidad, etc.

Mapa que utiliza este servicio, https://www.bicing.barcelona/es/mapa-de-disponibilidad-provisional

El archivo json que retorna el servicio tiene coordenadas pero no es un fichero GeoJSON. [^1]

Para ver estos datos sobre un mapa crearemos un visor utilizando Leaflet. [^2]

## Creación de un visor

- Crear una carpeta con el nombre de *visor-bicing*.
- Crear un archivo con el nombre de *index.html* dentro de la carpeta
- Abrir el archivo index.html con un editor de texto y copiar el siguiente código.

```html
<!DOCTYPE html>
<html>
<head>
  <title>Servicio de Bicing realtime</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <style>
    #map {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script type="text/javascript">
    var map = L.map('map');
    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  </script>
</body>
</html>
```

- Abrir el archivo index.html en el navegador para ver que carga un mapa centrado en Barcelona.

- Agregar el plugin para cargar datos en tiempo real. Para ellos utilizaremos el plugin Leaflet Realtime [^3].  Copiar lo siguiente justo después de cuando carguemos la librería de Leaflet.

```html hl_lines="20"
<!DOCTYPE html>
<html>
<head>
  <title>Servicio de Bicing realtime</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <style>
    #map {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <script type="text/javascript">
    var map = L.map('map');
    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  </script>
</body>
</html>
```

- Agregar la capa de realtime del bicing a nuestro mapa. Siguiendo el ejemplo básico del plugin para cagar una capa, copiar lo siguiente al final de nuestro código de javascript.

```html hl_lines="29 30 31 32 33 34 35"
<!DOCTYPE html>
<html>
<head>
  <title>Servicio de Bicing realtime</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <style>
    #map {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <script type="text/javascript">
    var map = L.map('map');
    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var realtime = L.realtime({
      url: 'https://www.bicing.barcelona/es/get-stations',
      crossOrigin: true,
      type: 'json'
    }, {
      interval: 10 * 1000
    }).addTo(map);
  </script>
</body>
</html>
```

- Recargar la página para visualizar nuestra capa de bicing. Observaremos que no aparece ningún dato. Abrir la consola de desarrollador del navegador presionando F12 y veremos que cada 3 segundos aparecerá un error. El error es: *<span style="color:red">Access to fetch at `https://www.bicing.barcelona/es/get-stations?_=1733770062417` from origin `http://127.0.0.1:5500` has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource</span>*. Este error es debido a que estamos llamando a un servicio que no está en nuestro dominio y por lo tanto da un error de CORS [^7]. Para evitar el error de CORS necesitamos un proxy [^8] en nuestro servidor web que pueda hacer la llamada al servicio de Bicing y que nos devuelva el contenido.

## Creación del proxy

Crearemos un proxy que nos permita hacer la llamada al servicio 

- Instalar Node.js. Descargar la última versión LTS y lo instalaremos con las opciones por defecto. Una vez instalado el Node abrir la consola para verificar que se ha instalado correctamente. Escribir

```bash
node -v
```

- Navegar hasta nuestra carpeta *visor-bicing-vt* y escribir:

```bash
npm init -y
```

Con este comando estaremos creando el archivo *package.json*. La opción -y acepta todas la opciones por defecto. Si no ponemos la opción -y este comando solicita varios elementos como, por ejemplo, el nombre y la versión de la aplicación. Sólo hay que pulsar ENTER para aceptar los valores predeterminados.

- Instalar las dependencias para crear nuestro servicio de proxy. En este caso utilizaremos Express como servidor web, el módulo axios y el módulo de cors.

- Instalar el express y los módulos y guardarlo en la lista de dependencias

```bash
npm install --save express axios cors
```

- Crear un archivo llamado *app.js* que servirá de proxy con el servicio de Bicing. Copiar lo siguiente en este archivo.

```js
var express  = require('express');
var app      = express();
var cors = require('cors');
var axios = require('axios');
var serverBicing = "https://www.bicing.barcelona/es/get-stations";
const port = 3000;

app.use(cors());
app.use(express.static('public'));

app.all("/bicingjson/*", function(req, res) {
  console.log('redirecting to Server2');
  //axios.get(serverBicing, { headers: { Authorization: `Bearer ${token}` } }).then(function(response){
  axios.get(serverBicing).then(function(response){
    // handle success
    res.send(response.data);
  }).catch(function (error) {
    console.log(error);
    res.send(error);
  });
});

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
});
```

- Probar que nuestro proxy está funcionando, escribiendo:

```bash
node app.js
```

- Abrir la url de nuestro proxy http://localhost:3000/bicingjson/ en el navegador.

### Modificar el visor

```html hl_lines="30"
<!DOCTYPE html>
<html>
<head>
  <title>Servicio de Bicing realtime</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <style>
    #map {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <script type="text/javascript">
    var map = L.map('map');
    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var realtime = L.realtime({
      url: 'http://localhost:3000/bicingjson/',
      crossOrigin: true,
      type: 'json'
    }, {
      interval: 10 * 1000
    }).addTo(map);
  </script>
</body>
</html>
```

- Recargar la página para visualizar nuestra capa de bicing. Observaremos que no aparece ningún dato. Abrir la consola de desarrollador del navegador presionando F12 y veremos que cada 3 segundos aparecerá un error. El error es Error: Invalid GeoJSON object.. Este error es debido a lo que ya comentamos; la respuesta del servicio de Bicing no es un GeoJSON.

- Crear una variable llamada geojson que será la que contendrá el GeoJSON resultante de la transformación, antes de la declaración de nuestra capa de realtime

```html hl_lines="29 30 31 32"
<!DOCTYPE html>
<html>
<head>
  <title>Servicio de Bicing realtime</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <style>
    #map {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <script type="text/javascript">
    var map = L.map('map');
    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var geojson = {
      type: 'FeatureCollection',
      features: []
    };

    var realtime = L.realtime({
      url: 'http://localhost:3000/bicingjson/',
      crossOrigin: true,
      type: 'json'
    }, {
      interval: 10 * 1000
    }).addTo(map);
  </script>
</body>
</html>
```

- Modificar la aplicación para transformar la respuesta del bicing en un GeoJSON. Modificar nuestra capa realtime con el siguiente código

```html hl_lines="34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63"
<!DOCTYPE html>
<html>
<head>
  <title>Servicio de Bicing realtime</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <style>
    #map {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <script type="text/javascript">
    var map = L.map('map');
    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var geojson = {
      type: 'FeatureCollection',
      features: []
    };

    var realtime = L.realtime(function(success, error) {
        fetch('http://localhost:3000/bicingjson/')
        .then(function(response) {
            return response.json();
        })
        .then(function(respuesta) {
            console.log(respuesta);
            var stations = respuesta.stations;
            for (var i = stations.length - 1; i >= 0; i--) {
                var station = stations[i];
                var feature = {
                    type: 'Feature',
                    properties: {
                        id: station.id,
                        address: station.streetName,
                        capacity: station.slots + station.bikes
                    },
                    geometry: {
                        type: 'Point',
                        coordinates: [station.longitude, station.latitude]
                    }
                };
                geojson.features.push(feature);
            }
            success(geojson);
        })
        .catch(error);
    }, {
        interval: 10 * 1000
    }).addTo(map);
  </script>
</body>
</html>
```

- Recargar la aplicación y veremos los puntos de las estaciones de bicing. Si vamos a la pestaña de red (network) en la consola de desarrollador del navegador podremos ver que cada 3 segundos se hace una llamada al servicio.

- Crear un popup para ver la información de la estación al seleccionarla. Escribir justo después de donde definimos el intervalo

```html hl_lines="61 62 63 64 65 66 67 68"
<!DOCTYPE html>
<html>
<head>
  <title>Servicio de Bicing realtime</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <style>
    #map {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-realtime/2.2.0/leaflet-realtime.min.js"></script>
  <script type="text/javascript">
    var map = L.map('map');
    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var geojson = {
      type: 'FeatureCollection',
      features: []
    };

        var realtime = L.realtime(function(success, error) {
        fetch('http://localhost:3000/bicingjson/')
        .then(function(response) {
            return response.json();
        })
        .then(function(respuesta) {
            var stations = respuesta.stations;
            for (var i = stations.length - 1; i >= 0; i--) {
                var station = stations[i];
                var feature = {
                    type: 'Feature',
                    properties: {
                        id: station.id,
                        address: station.streetName,
                        capacity: station.slots + station.bikes
                    },
                    geometry: {
                        type: 'Point',
                        coordinates: [station.longitude, station.latitude]
                    }
                };
                geojson.features.push(feature);
            }
            success(geojson);
        })
        .catch(error);
    }, {
        interval: 10 * 1000,
        onEachFeature(f, l) {
            l.bindPopup(function() {
                return '<h3>' + f.properties.id + '</h3>' +
                    '<p>' + f.properties.address + '</p>' +
                    '<p>capacity: <strong>' + f.properties.capacity + '</strong></p>';
            });
        }
    }).addTo(map);
  </script>
</body>
</html>
```

- Recargar la página y hacer click sobre alguna estación para ver su información en tiempo real.

![mapa de servicio de bicing](img/mapa_bicing.png)
*mapa de servicio de bicing*

## Referencias

[^1]: https://es.wikipedia.org/wiki/GeoJSON
[^2]: http://leafletjs.com/
[^3]: https://github.com/perliedman/leaflet-realtime
[^7]: https://developer.mozilla.org/es/docs/Web/HTTP/Access_control_CORS
[^8]: https://es.wikipedia.org/wiki/Servidor_proxy
