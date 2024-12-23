# Ejemplo GTFS

## ¿Qué es la GTFS?

La Especificación general de feeds de transporte público (GTFS) define un formato común para los horarios de transporte público y la información geográfica asociada a ellos. Los "feeds" GTFS permiten que las empresas de transporte público publiquen sus datos de transporte y que los programadores escriban aplicaciones que consuman esos datos de manera interoperable [^1].

## Creación de un visor que muestre las líneas y paradas de un GTFS

Para crear un visor de mapas utilizaremos la librería de mapas Leaflet [^2]. Y cargaremos los datos de portal de la Plataforma VLCi (Valencia SmartCity) [^3]     

- Crear una carpeta con el nombre de *visor-gtfs*.

- Crear una carpeta con el nombre de *public* dentro de la carpeta visor-gtfs.

- Crear un archivo con el nombre de *index.html* dentro de la carpeta public.

- Abrir el archivo index.html con un editor de texto y copiar el siguiente código.

```html
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="X-UA-Compatible" content="ie=edge">
	<title>Ejemplo GTFS</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
	<style>
		#map {
			height: 100%;
			width: 100%;
			position: absolute;
		}
	</style>
</head>
<body>

	<div id="map">

	</div>

	<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
	<script>
		var map = L.map('map');

		map.setView([39.4652, -0.3861], 13);  

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);
	</script>
</body>
</html>
```

- Abrir el archivo index.html en el navegador para confirmar que se carga un mapa centrado en Valencia.

## Crear el proxy

- Crear un archivo con el nombre de *package.json* dentro de la carpeta.

- Abrir el archivo package.json con un editor de texto y copiar el siguiente código.

```js
{
	"name": "visor-gtfs",
	"version": "1.0.0",
	"description": "",
	"main": "index.js",
	"scripts": {
		"test": "echo \"Error: no test specified\" && exit 1"
	},
	"author": "",
	"license": "ISC",
	"dependencies": {
		"assert": "^2.0.0",
		"cors": "^2.8.5",
		"express": "^4.17.1",
		"fast-csv": "^3.4.0",
		"request": "^2.88.0",
		"yauzl": "^2.10.0"
	}
}
```

- Instalar Node.js [^4]. Descargar la última versión LTS y lo instalaremos con las opciones por defecto. Abrir la consola para verificar que se ha instalado correctamente y escribir

```bash
node -v
```

- Navegar hasta nuestra carpeta *visor-gtfs* y escribir:

```bash
npm install
```

Con este comando estamos instalando las dependencias declaradas en el archivo *package.json*

Al ejecutar estos comandos veremos que se crea una carpeta llamada *node_modules* donde se guardan los módulos instalados.

- Instalar el módulo nodemon [^8] de manera global.

```bash
npm install -g nodemon
```

- Crear un archivo llamado *app.js* que servirá de proxy con el servicio GTFS. Copiar lo siguiente en este archivo.

```js
var express  = require('express');
var app      = express();
var cors = require('cors');
var request = require('request');
var path = require('path');
var https = require('https');
var fs = require('fs');
var yauzl = require("yauzl");

app.use(cors());
app.use(express.static('public'));

app.listen(3000);
```

- Probar que nuestro proxy está funcionando, escribir:

```bash
nodemon app.js
```

- Escribir en el navegador http://localhost:3000 y ver nuestro mapa.

- Crear un archivo llamado *gtfs2geojson.js*. Copiar en el archivo el código del siguiente enlace https://raw.githubusercontent.com/andrewharvey/gtfs2geojson/master/index.js este código convierte datos de un GTFS en un GeoJSON. Código basado en la librería https://github.com/andrewharvey/gtfs2geojson

- Cargar en archivo en nuestra app.js. Escribir lo siguiente justo después de donde se carga el módulo yauzl

```js hl_lines="9"
var express  = require('express');
var app      = express();
var cors = require('cors');
var request = require('request');
var path = require('path');
var https = require('https');
var fs = require('fs');
var yauzl = require("yauzl");
var gtfs2geojson = require('./gtfs2geojson.js');

app.use(cors());
app.use(express.static('public'));

app.listen(3000);
```

- Crear la variable que contiene la url del servicio GTFS de Líneas, paradas, horarios de autobuses de la EMT de Valencia [^5]. Escribir lo siguiente justo después de la variable *gtfs2geojson*

```js hl_lines="11"
var express  = require('express');
var app      = express();
var cors = require('cors');
var request = require('request');
var path = require('path');
var https = require('https');
var fs = require('fs');
var yauzl = require("yauzl");
var gtfs2geojson = require('./gtfs2geojson.js');

const url = 'https://opendata.vlci.valencia.es/dataset/ab058cf8-ad3e-4d9c-ac89-0c6367ecf351/resource/c81b69e6-c082-44dc-acc6-66fc417b4e66/download/google_transit.zip';

app.use(cors());
app.use(express.static('public'));

app.listen(3000);
```

- Crear una función llamada getZip para descargar un archivo. La función recibe como parámetro una url. Escribir lo siguiente al final del archivo app.js

```js hl_lines="18 19 20 21 22 23 24 25 26 27 28"
var express  = require('express');
var app      = express();
var cors = require('cors');
var request = require('request');
var path = require('path');
var https = require('https');
var fs = require('fs');
var yauzl = require("yauzl");
var gtfs2geojson = require('./gtfs2geojson.js');

const url = 'https://opendata.vlci.valencia.es/dataset/ab058cf8-ad3e-4d9c-ac89-0c6367ecf351/resource/c81b69e6-c082-44dc-acc6-66fc417b4e66/download/google_transit.zip';

app.use(cors());
app.use(express.static('public'));

app.listen(3000);

function getZip(url){
	return new Promise(function (resolve, reject) {
		var file = fs.createWriteStream("gtfs.zip");
		var request = https.get(url, function(response) {
			response.pipe(file);
		});
		file.on('finish', function(){
			resolve();
		});
	}); 
}
```

- Crear una función que extrae un archivo de un zip. La función recibe como parámetro el nombre del archivo que se desea extraer. Escribir lo siguiente al final del archivo app.js

```js hl_lines="30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59"
var express  = require('express');
var app      = express();
var cors = require('cors');
var request = require('request');
var path = require('path');
var https = require('https');
var fs = require('fs');
var yauzl = require("yauzl");
var gtfs2geojson = require('./gtfs2geojson.js');

const url = 'https://opendata.vlci.valencia.es/dataset/ab058cf8-ad3e-4d9c-ac89-0c6367ecf351/resource/c81b69e6-c082-44dc-acc6-66fc417b4e66/download/google_transit.zip';

app.use(cors());
app.use(express.static('public'));

app.listen(3000);

function getZip(url){
	return new Promise(function (resolve, reject) {
		var file = fs.createWriteStream("gtfs.zip");
		var request = https.get(url, function(response) {
			response.pipe(file);
		});
		file.on('finish', function(){
			resolve();
		});
	}); 
}

function leerZip(archivo){
	return new Promise(function (resolve, reject) {
		yauzl.open('gtfs.zip', {lazyEntries: true}, function(err, zipfile) {
			if (err) throw err;
			zipfile.readEntry();
			zipfile.on("entry", function(entry) {
			if (/\/$/.test(entry.fileName)) {
				// Directory file names end with '/'.
				// Note that entires for directories themselves are optional.
				// An entry's fileName implicitly requires its parent directories to exist.
				zipfile.readEntry();
			} else {
				// file entry
				if(entry.fileName === archivo){
				zipfile.openReadStream(entry, function(err, readStream) {
					if (err) throw err;
					var file = fs.createWriteStream(entry.fileName);
					readStream.pipe(file); 
					file.on('finish', function(){
						resolve();
					});
				});
				}else{
				zipfile.readEntry();
				}
			}
			});
		});
	}); 
}
```

- Descargar el archivo GTFS y guardarlo en el ordenador. Escribir lo siguiente justo antes de la línea donde definimos el puerto por el cual escucha nuestro servidor

```js hl_lines="16 17 18 19 20 21 22"
var express  = require('express');
var app      = express();
var cors = require('cors');
var request = require('request');
var path = require('path');
var https = require('https');
var fs = require('fs');
var yauzl = require("yauzl");
var gtfs2geojson = require('./gtfs2geojson.js');

const url = 'https://opendata.vlci.valencia.es/dataset/ab058cf8-ad3e-4d9c-ac89-0c6367ecf351/resource/c81b69e6-c082-44dc-acc6-66fc417b4e66/download/google_transit.zip';

app.use(cors());
app.use(express.static('public'));

app.all("/getdata/*", function(req, res) {
	getZip(url).then(function(){
		Promise.all([leerZip('shapes.txt'),leerZip('stops.txt')]).then(values => {
			res.json({"msg": "archivos descargados"});
		});
	});
});

app.listen(3000);

function getZip(url){
	return new Promise(function (resolve, reject) {
		var file = fs.createWriteStream("gtfs.zip");
		var request = https.get(url, function(response) {
			response.pipe(file);
		});
		file.on('finish', function(){
			resolve();
		});
	}); 
}

function leerZip(archivo){
	return new Promise(function (resolve, reject) {
		yauzl.open('gtfs.zip', {lazyEntries: true}, function(err, zipfile) {
			if (err) throw err;
			zipfile.readEntry();
			zipfile.on("entry", function(entry) {
			if (/\/$/.test(entry.fileName)) {
				// Directory file names end with '/'.
				// Note that entires for directories themselves are optional.
				// An entry's fileName implicitly requires its parent directories to exist.
				zipfile.readEntry();
			} else {
				// file entry
				if(entry.fileName === archivo){
				zipfile.openReadStream(entry, function(err, readStream) {
					if (err) throw err;
					var file = fs.createWriteStream(entry.fileName);
					readStream.pipe(file); 
					file.on('finish', function(){
						resolve();
					});
				});
				}else{
				zipfile.readEntry();
				}
			}
			});
		});
	}); 
}
```

- Abrir la url http://localhost:3000/getdata/ en el navegador para comprobar que se han descargado correctamente los archivos *gtfs.zip*, *shapes.txt* y *stops.txt*.

- Leer los archivos GTFS y convertirlos a GeoJson. Escribir lo siguiente justo antes de la línea donde definimos el puerto por el cual escucha nuestro servidor

```js hl_lines="24 25 26 27 28 29 30 31 32 33 34"
var express  = require('express');
var app      = express();
var cors = require('cors');
var request = require('request');
var path = require('path');
var https = require('https');
var fs = require('fs');
var yauzl = require("yauzl");
var gtfs2geojson = require('./gtfs2geojson.js');

const url = 'https://opendata.vlci.valencia.es/dataset/ab058cf8-ad3e-4d9c-ac89-0c6367ecf351/resource/c81b69e6-c082-44dc-acc6-66fc417b4e66/download/google_transit.zip';

app.use(cors());
app.use(express.static('public'));

app.all("/getdata/*", function(req, res) {
	getZip(url).then(function(){
		Promise.all([leerZip('shapes.txt'),leerZip('stops.txt')]).then(values => {
			res.json({"msg": "archivos descargados"});
		});
	});
});

app.all("/stops/*", function(req, res) {
	gtfs2geojson.stops(fs.readFileSync('stops.txt', 'utf8'), function(result){
		res.json(result);
	});
});

app.all("/shapes/*", function(req, res) {
	gtfs2geojson.lines(fs.readFileSync('shapes.txt', 'utf8'), function(result){
		res.json(result);
	});
});

app.listen(3000);

function getZip(url){
	return new Promise(function (resolve, reject) {
		var file = fs.createWriteStream("gtfs.zip");
		var request = https.get(url, function(response) {
			response.pipe(file);
		});
		file.on('finish', function(){
			resolve();
		});
	}); 
}

function leerZip(archivo){
	return new Promise(function (resolve, reject) {
		yauzl.open('gtfs.zip', {lazyEntries: true}, function(err, zipfile) {
			if (err) throw err;
			zipfile.readEntry();
			zipfile.on("entry", function(entry) {
			if (/\/$/.test(entry.fileName)) {
				// Directory file names end with '/'.
				// Note that entires for directories themselves are optional.
				// An entry's fileName implicitly requires its parent directories to exist.
				zipfile.readEntry();
			} else {
				// file entry
				if(entry.fileName === archivo){
				zipfile.openReadStream(entry, function(err, readStream) {
					if (err) throw err;
					var file = fs.createWriteStream(entry.fileName);
					readStream.pipe(file); 
					file.on('finish', function(){
						resolve();
					});
				});
				}else{
				zipfile.readEntry();
				}
			}
			});
		});
	}); 
}
```

- Abrir la url http://localhost:3000/stops/ en el navegador para comprobar que se muestra un GeoJson con la información de las paradas. 

## Modificar el mapa

- Cargar este JSON en nuestro mapa utilizando un plugin de Leaflet llamado *leaflet-ajax* [^6]. Este plugin permite hacer una llamada AJAX a un servicio que retorne un JSON y cargar la respuesta en un mapa. Para cargar este plugin debemos agregar lo siguiente justo después de donde hemos cargado el leaflet

```html hl_lines="24"
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="X-UA-Compatible" content="ie=edge">
	<title>Ejemplo GTFS</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
	<style>
		#map {
			height: 100%;
			width: 100%;
			position: absolute;
		}
	</style>
</head>
<body>

	<div id="map">

	</div>

	<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-ajax/2.1.0/leaflet.ajax.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
	<script>
		var map = L.map('map');

		map.setView([39.4652, -0.3861], 13);  

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);
	</script>
</body>
</html>
```

- Utilizar el plugin para agregar la capa de paradas al mapa llamando a nuestro servidor. Agregar lo siguiente al final de nuestro código:

```html hl_lines="34 35 36 37 38 39 40 41 42 43 44 45 46 47 48"
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="X-UA-Compatible" content="ie=edge">
	<title>Ejemplo GTFS</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
	<style>
		#map {
			height: 100%;
			width: 100%;
			position: absolute;
		}
	</style>
</head>
<body>

	<div id="map">

	</div>

	<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-ajax/2.1.0/leaflet.ajax.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
	<script>
		var map = L.map('map');

		map.setView([39.4652, -0.3861], 13);  

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);

		var geojsonParadas = new L.GeoJSON.AJAX('/stops/',{
            pointToLayer: function (feature, latlng) {                    
                return new L.CircleMarker(latlng, {
                    radius: 5,
                    fillColor: "#A30000",
                    color: "#A30000",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            },
            onEachFeature: function (feature, layer) {
                layer.bindPopup(feature.properties.stop_name);
            }
        }).addTo(map);
	</script>
</body>
</html>
```

- Recargar el mapa y comprobar que aparecen los puntos de las paradas en el mapa.

- Utilizar el plugin para agregar la capa de líneas al mapa llamando a nuestro servidor. Agregar lo siguiente al final de nuestro código:

```html hl_lines="50 51 52"
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="X-UA-Compatible" content="ie=edge">
	<title>Ejemplo GTFS</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
	<style>
		#map {
			height: 100%;
			width: 100%;
			position: absolute;
		}
	</style>
</head>
<body>

	<div id="map">

	</div>

	<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-ajax/2.1.0/leaflet.ajax.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
	<script>
		var map = L.map('map');

		map.setView([39.4652, -0.3861], 13);  

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);

		var geojsonParadas = new L.GeoJSON.AJAX('/stops/',{
            pointToLayer: function (feature, latlng) {                    
                return new L.CircleMarker(latlng, {
                    radius: 5,
                    fillColor: "#A30000",
                    color: "#A30000",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            },
            onEachFeature: function (feature, layer) {
                layer.bindPopup(feature.properties.stop_name);
            }
        }).addTo(map);

		var geojsonLineas = new L.GeoJSON.AJAX('/shapes/',{
           
        }).addTo(map);
	</script>
</body>
</html>
```

- Recargar el mapa y comprobar que aparecen las líneas del bus en el mapa.

- Cargar la librería de manipulación de colores **chroma.js** [^7]. Escribir lo siguiente después de donde cargamos el plugin de leaflet.ajax

```html hl_lines="25"
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="X-UA-Compatible" content="ie=edge">
	<title>Ejemplo GTFS</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
	<style>
		#map {
			height: 100%;
			width: 100%;
			position: absolute;
		}
	</style>
</head>
<body>

	<div id="map">

	</div>

	<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-ajax/2.1.0/leaflet.ajax.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.0.6/chroma.min.js"></script>
	<script>
		var map = L.map('map');

		map.setView([39.4652, -0.3861], 13);  

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);

		var geojsonParadas = new L.GeoJSON.AJAX('/stops/',{
            pointToLayer: function (feature, latlng) {                    
                return new L.CircleMarker(latlng, {
                    radius: 5,
                    fillColor: "#A30000",
                    color: "#A30000",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            },
            onEachFeature: function (feature, layer) {
                layer.bindPopup(feature.properties.stop_name);
            }
        }).addTo(map);

		var geojsonLineas = new L.GeoJSON.AJAX('/shapes/',{
           
        }).addTo(map);
	</script>
</body>
</html>
```

- Dar estilo a la capa de líneas generando un color aleatorio. Escribir lo siguiente en las opciones de la capa geojsonLineas

```html hl_lines="52 53 54"
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="X-UA-Compatible" content="ie=edge">
	<title>Ejemplo GTFS</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
	<style>
		#map {
			height: 100%;
			width: 100%;
			position: absolute;
		}
	</style>
</head>
<body>

	<div id="map">

	</div>

	<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-ajax/2.1.0/leaflet.ajax.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.0.6/chroma.min.js"></script>
	<script>
		var map = L.map('map');

		map.setView([39.4652, -0.3861], 13);  

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);

		var geojsonParadas = new L.GeoJSON.AJAX('/stops/',{
            pointToLayer: function (feature, latlng) {                    
                return new L.CircleMarker(latlng, {
                    radius: 5,
                    fillColor: "#A30000",
                    color: "#A30000",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            },
            onEachFeature: function (feature, layer) {
                layer.bindPopup(feature.properties.stop_name);
            }
        }).addTo(map);

		var geojsonLineas = new L.GeoJSON.AJAX('/shapes/',{
           	style: function(geoJsonFeature){
            	return {color: chroma.random(), opacity: 0.5};
       		}
        }).addTo(map);
	</script>
</body>
</html>
```
	
- Recargar el mapa y comprobar que aparecen las líneas del bus en el mapa con colores aleatorios.

![ejemplo gtfs](img/mapa_gtfs.png)
*ejemplo gtfs*

!!! question "Ejercicios 2,5 pts"
	1. Mostrar un popup con información de la propiedad *shape_id* al hacer click en la capa de líneas (1 pt)
	
	2. Cargar datos del gtfs de FGC https://www.fgc.cat/es/opendata/  
	En el siguiente enlace está el fichero de gtfs https://www.fgc.cat/wp-content/uploads/2018/02/google_transit.zip (1 pt)

	3. Centrar el mapa en Barcelona (0,5 pt)

## Referencias

[^1]: https://developers.google.com/transit/gtfs/?hl=es-419
[^2]: http://leafletjs.com/
[^3]: https://opendata.vlci.valencia.es
[^4]: https://nodejs.org/es/
[^5]: http://gobiernoabierto.valencia.es/es/dataset/?id=google-transit-lineas-paradas-horarios-de-autobuses
[^6]: https://github.com/calvinmetcalf/leaflet-ajax
[^7]: https://github.com/gka/chroma.js/
