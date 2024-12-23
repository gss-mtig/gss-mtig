# Ejemplo Geocodificador

La geocodificación de direcciones consiste en la localización espacial de una dirección específica.

Existen dos tipos de geocodificación: 

* **directa** es la obtención de coordenadas a partir de una dirección postal
* **inversa** es la localización de direcciones a partir de coordenadas geográficas

## Creación de un visor que permita buscar direcciones y topónimos

Para crear un visor de mapas utilizaremos la librería de mapas Leaflet [^1]. Y cargaremos los datos del Geocodificador del OpenCage [^2]

- Crear una carpeta con el nombre de *visor-geocoder*.

- Crear un archivo con el nombre de *index.html* dentro de la carpeta.

- Abrir el archivo index.html con un editor de texto y copiar el siguiente código.

```html
<!DOCTYPE html>
<html>
<head>
  <title>Ejemplo geocoder</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
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

-  Abrir el archivo index.html en el navegador para comprobar que se carga un mapa centrado en Barcelona.

- Agregar el plugin al mapa

```html hl_lines="7 8 31 32 33 34 35"
<!DOCTYPE html>
<html>
<head>
  <title>Ejemplo geocoder</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/css/L.Control.OpenCageGeocoding.min.css" />
  <script src="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/js/L.Control.OpenCageGeocoding.min.js"></script>
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

  <script type="text/javascript">
    var map = L.map('map');

    map.setView([41.3887, 2.1777], 13);
    
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

     var options = {
      key: 'YOUR-API-KEY',
      limit: 10,
    };
    var control = L.Control.openCageGeocoding(options).addTo(map);
  
  </script>
</body>
</html>
```

- Recargamos el mapa en el navegador y podemos ver que nos aparece una caja de búsqueda en el mapa

![ejemplo geocodificador](img/ejemplo_geocoder.png)
*ejemplo geocodificador*

## Geocodificación inversa

Implementaremos la funcionalidad que cuando el usuario haga click en el mapa se busque la dirección o topónimo más cercano.

- Capturar el evento click en el mapa.

```html hl_lines="37 38 39"
<!DOCTYPE html>
<html>
<head>
  <title>Ejemplo geocoder</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/css/L.Control.OpenCageGeocoding.min.css" />
  <script src="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/js/L.Control.OpenCageGeocoding.min.js"></script>
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

  <script type="text/javascript">
    var map = L.map('map');

    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var options = {
      key: 'YOUR-API-KEY',
      limit: 10,
    };
    var control = L.Control.openCageGeocoding(options).addTo(map);

    map.on('click', function(e){
      console.log(e);
    });

  </script>
</body>
</html>
```

- Recargar la aplicación y abrir la consola del desarrollador, al hacer click sobre el mapa ver que en la consola aparece el objeto del evento click. Inspeccionar este objeto para ver que tiene una propiedad llamada latlng que contiene las coordenadas donde se ha hecho el click.

- Llamar al servicio de geocodificación pasándole las coordenadas del click para obtener los elementos

```html hl_lines="39 40 41 42 43 44 45 46 47 48"
<!DOCTYPE html>
<html>
<head>
  <title>Ejemplo geocoder</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/css/L.Control.OpenCageGeocoding.min.css" />
  <script src="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/js/L.Control.OpenCageGeocoding.min.js"></script>
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

  <script type="text/javascript">
    var map = L.map('map');

    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var options = {
      key: 'YOUR-API-KEY',
      limit: 10,
    };
    var control = L.Control.openCageGeocoding(options).addTo(map);

    map.on('click', function(e){
      console.log(e);
      var url = `https://api.opencagedata.com/geocode/v1/json?q=${e.latlng.lat}+${e.latlng.lng}&key=${options.key}`;
      fetch(url)
      .then(function(response) {
        response.json().then(function(data){
          console.log(data);
      });
      })
      .catch(function(myJson) {
        console.log(myJson);
      });
    });

  </script>
</body>
</html>
```

- Recargar la aplicación y abrir la consola del desarrollador, al hacer click sobre el mapa ver que en la consola aparece el objeto de respuesta del geocodificador. 

- Al recibir la respuesta mostrar un marcador en el mapa en la posición donde el usuario hizo el click.

```html hl_lines="44 45"
<!DOCTYPE html>
<html>
<head>
  <title>Ejemplo geocoder</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/css/L.Control.OpenCageGeocoding.min.css" />
  <script src="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/js/L.Control.OpenCageGeocoding.min.js"></script>
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

  <script type="text/javascript">
    var map = L.map('map');

    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var options = {
      key: 'YOUR-API-KEY',
      limit: 10,
    };
    var control = L.Control.openCageGeocoding(options).addTo(map);

    map.on('click', function(e){
      console.log(e);
      var url = `https://api.opencagedata.com/geocode/v1/json?q=${e.latlng.lat}+${e.latlng.lng}&key=${options.key}`;
      fetch(url)
      .then(function(response) {
        response.json().then(function(data){
          console.log(data);
          var marker = new L.marker(e.latlng);
          map.addLayer(marker);
      });
      })
      .catch(function(myJson) {
        console.log(myJson);
      });
    });

  </script>
</body>
</html>
```

- Recargar el mapa y ver que aparece un marcador al hacer click sobre el mapa.

- Mostrar la etiqueta con la dirección retornada de la primera respuesta del geocodificador.

```html hl_lines="44 45 47"
<!DOCTYPE html>
<html>
<head>
  <title>Ejemplo geocoder</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/css/L.Control.OpenCageGeocoding.min.css" />
  <script src="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/js/L.Control.OpenCageGeocoding.min.js"></script>
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

  <script type="text/javascript">
    var map = L.map('map');

    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var options = {
      key: 'YOUR-API-KEY',
      limit: 10,
    };
    var control = L.Control.openCageGeocoding(options).addTo(map);

    map.on('click', function(e){
      console.log(e);
      var url = `https://api.opencagedata.com/geocode/v1/json?q=${e.latlng.lat}+${e.latlng.lng}&key=${options.key}`;
      fetch(url)
      .then(function(response) {
        response.json().then(function(data){
          console.log(data);
          var etiqueta = data.results[0].formatted;
          var marker = new L.marker(e.latlng).bindPopup(etiqueta);
          map.addLayer(marker);
          marker.openPopup();
      });
      })
      .catch(function(myJson) {
        console.log(myJson);
      });
    });

  </script>
</body>
</html>
```

- Recargar el mapa y ver que aparece la etiqueta.

![ejemplo etiqueta geocodificador](img/ejemplo_geocoder_etiqueta.png)
*ejemplo etiqueta geocodificador*

- Mostrar el marcador en la posición de la primera respuesta del geocodificador y no en la posición del click

```html hl_lines="45 46"
<!DOCTYPE html>
<html>
<head>
  <title>Ejemplo geocoder</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/css/L.Control.OpenCageGeocoding.min.css" />
  <script src="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.0.0/dist/js/L.Control.OpenCageGeocoding.min.js"></script>
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

  <script type="text/javascript">
    var map = L.map('map');

    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var options = {
      key: 'YOUR-API-KEY',
      limit: 10,
    };
    var control = L.Control.openCageGeocoding(options).addTo(map);

    map.on('click', function(e){
      console.log(e);
      var url = `https://api.opencagedata.com/geocode/v1/json?q=${e.latlng.lat}+${e.latlng.lng}&key=${options.key}`;
      fetch(url)
      .then(function(response) {
        response.json().then(function(data){
          console.log(data);
          var etiqueta = data.results[0].formatted;
          var posicion = data.results[0].geometry;
          var marker = new L.marker(posicion).bindPopup(etiqueta);
          map.addLayer(marker);
          marker.openPopup();
      });
      })
      .catch(function(myJson) {
        console.log(myJson);
      });
    });

  </script>
</body>
</html>
```

- Recargar el mapa y hacer click sobre el mapa. Vemos que se nos muestra un marcador con la etiqueta en una posición cercana a donde hemos hecho click.

!!! question "Ejercicios 2 pts"
	1. Mostrar la propiedad **components.municipality** junto con la dirección en la etiqueta (1 pt)

    	2. **Extra**: Mostrar el grado de confianza de la respuesta *confidence*, la categoría *components._category* y el tipo *components._type*. (1 pt). Ejemplo:
  		<div><b>Confianza:</b>9<br><b>Categoría:</b>outdoors/recreation<br><b>Tipo:</b>leisure</div>


## Referencias

[^1]: http://leafletjs.com/
[^2]: https://opencagedata.com/
