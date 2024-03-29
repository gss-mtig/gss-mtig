#Ejemplo servicio realtime para compartir la ubicación

Simularemos un servicio que permita compartir la ubicación de los usuarios y ver que usuarios están en linea. Para ello utilizaremos la librería Socket.io [^1] que permite la comunicación en tiempo real en dos direcciones cliente-servidor (tipo pull) y servidor-cliente (tipo push). Esto lo hace gracias a un socket [^2].

Para mostrar los datos en el mapa utilizaremos la librería Leaflet [^3]. Para obtener la ubicación de los usuarios podemos usar el plugin *leaflet-locatecontrol* [^4], en nuestro caso vamos a simular la ubicación del usuario haciendo click sobre el mapa en lugar de utilizar la ubicación del usuario.

## Creación del mapa

- Crear una carpeta con el nombre de *user-realtime*.

- Crear una carpeta con el nombre de *public* dentro de la carpeta user-realtime.

- Crear un archivo con el nombre de *index.html* dentro de la carpeta public.

- Abrir el archivo index.html con un editor de texto y copiar el siguiente código.

```html
<!DOCTYPE html>
<html>
<head>
	<title>Servicio compartir ubicación realtime</title>
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

-  Abrir el archivo index.html en el navegador para comprobar que se carga un mapa centrado en Barcelona.

- Capturar el evento click en el mapa. Luego de la declaración de nuestra capa escribir los siguiente:

```html hl_lines="30 31 32"
<!DOCTYPE html>
<html>
<head>
	<title>Servicio compartir ubicación realtime</title>
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
		
		map.on('click', function(e){
            console.log(e);
		});

		</script>
</body>
</html>
```

- Recargar la aplicación y abrir la consola del desarrollador, al hacer click sobre el mapa ver que en la consola aparece el objeto del evento click. Inspeccionar este objeto para ver que tiene una propiedad llamada latlng que contiene las coordenadas donde se ha hecho el click.

## Creación del servicio que comparte la ubicación de los usuarios

- Utilizaremos Node.js [^5] para implementar nuestro servidor web y utilizaremos el módulo de socket.io para establecer la comunicación entre el cliente y nuestro servidor.

- Instalar Node.js. Descargar la última versión LTS y lo instalaremos con las opciones por defecto. Una vez instalado el Node abrir la consola para verificar que se ha instalado correctamente. Escribir

```bash
node -v
```

- Navegar hasta nuestra carpeta *user-realtime* y escribir:

```bash
npm init -y 
```

Con este comando estaremos creando el archivo *package.json* con los valores predeterminados.

- Instalar las dependencias para crear nuestro servicio de proxy. En este caso utilizaremos Express [^6] como servidor web, el módulo socket.io [^7] y el módulo de cors [^8].

- Instalar el express y guardarlo en la lista de dependencias

```bash
npm install --save express socket.io cors
```

Al ejecutar estos comandos veremos que se crea una carpeta llamada *node_modules* donde se guardan los módulos instalados.

- Instalar el módulo nodemon [^8] de manera global.

```bash
npm install -g nodemon
```

- Crear un archivo llamado *app.js* que contendrá nuestra aplicación que servirá de servidor web. Para ello copiar lo siguiente en este archivo.

```js
var express  = require('express');
var app = express();
var cors = require('cors');
var http = require('http').Server(app);
var io = require('socket.io')(http);

app.use(cors());
app.use(express.static('public'));

io.on('connection', function(socket){
	console.log('a user connected');
});

http.listen(3000, function(){
	console.log('listening on *:3000');
});
```

- Probar que nuestro servidor está funcionando, escribiendo:

```bash
nodemon app.js
```

- Abrir la url de nuestro servidor http://localhost:3000/ en el navegador para ver nuestro mapa.

## Modificar el mapa

- Agregar la librería cliente de socket.io. Escribir en el archivo *index.html* justo debajo de donde cargamos el leaflet

```html hl_lines="20"
<!DOCTYPE html>
<html>
<head>
	<title>Servicio compartir ubicación realtime</title>
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
		<script src="https://cdn.jsdelivr.net/npm/socket.io-client@4.4.0/dist/socket.io.min.js"></script>
		<script type="text/javascript">
			var map = L.map('map');

			map.setView([41.3887, 2.1777], 13);
			

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
				attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);
		
		map.on('click', function(e){
            console.log(e);
		});

		</script>
</body>
</html>
```

- Declarar la variable que va a tener el objeto socket.io al inicio de nuestro código antes de la declaración del mapa escribir los siguiente:

```html hl_lines="22"
<!DOCTYPE html>
<html>
<head>
	<title>Servicio compartir ubicación realtime</title>
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
		<script src="https://cdn.jsdelivr.net/npm/socket.io-client@4.4.0/dist/socket.io.min.js"></script>
		<script type="text/javascript">
			var socket = io();
			
			var map = L.map('map');

			map.setView([41.3887, 2.1777], 13);
			

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
				attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);
		
		map.on('click', function(e){
            console.log(e);
		});

		</script>
</body>
</html>
```

- Recargar la página y ver que en la consola aparece el mensaje de *a user connected*.

- Enviar el evento click al servidor. En la función que se llama al hacer click sobre el mapa escribir los siguiente para enviar un evento al servidor. Este evento lo llamaremos *user_click* y le pasaremos como parámetro la posición del click.

```html hl_lines="35"
<!DOCTYPE html>
<html>
<head>
	<title>Servicio compartir ubicación realtime</title>
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
		<script src="https://cdn.jsdelivr.net/npm/socket.io-client@4.4.0/dist/socket.io.min.js"></script>
		<script type="text/javascript">
			var socket = io();
			
			var map = L.map('map');

			map.setView([41.3887, 2.1777], 13);
			

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
				attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);
		
		map.on('click', function(e){
			console.log(e);
			socket.emit('user_click', e.latlng);
		});

		</script>
</body>
</html>
```

## Modificar el servidor

- Escuchar al evento *user_click* en nuestra aplicación del servidor. Dentro de la función que se llama en el *io.on* es donde se crea el socket de conexión, por lo tanto escribir nuestro código dentro de la misma. Debajo de donde escribimos el mensaje de *a user connected* escribir lo siguiente:

```js hl_lines="12 13 14"
var express  = require('express');
var app = express();
var cors = require('cors');
var http = require('http').Server(app);
var io = require('socket.io')(http);

app.use(cors());
app.use(express.static('public'));

io.on('connection', function(socket){
	console.log('a user connected');
	socket.on('user_click', function(msg){
		console.log(msg);
	});
});

http.listen(3000, function(){
	console.log('listening on *:3000');
});
```

- Recargar la página y hacer click sobre el mapa para ver que en la consola aparece las coordenadas del click. Con esto ya hemos logrado la comunicación cliente-servidor.

- Lograr la comunicación servidor-cliente y que el servidor notifique a todos los cliente para esto debemos emitir un evento en nuestro servidor. Este evento lo llamaremos *new_user*. Copiar lo siguiente para emitir el evento dentro de la función que se llama en el evento *user_click*.

```js hl_lines="14"
var express  = require('express');
var app = express();
var cors = require('cors');
var http = require('http').Server(app);
var io = require('socket.io')(http);

app.use(cors());
app.use(express.static('public'));

io.on('connection', function(socket){
	console.log('a user connected');
	socket.on('user_click', function(msg){
		console.log(msg);
		io.emit('new_user', msg);
	});
});

http.listen(3000, function(){
	console.log('listening on *:3000');
});
```
## Modificar el mapa

- Escuchar el evento *new_user* en nuestro cliente. Al final de nuestro código html escribir

```html hl_lines="38 39 40"
<!DOCTYPE html>
<html>
<head>
	<title>Servicio compartir ubicación realtime</title>
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
		<script src="https://cdn.jsdelivr.net/npm/socket.io-client@4.4.0/dist/socket.io.min.js"></script>
		<script type="text/javascript">
			var socket = io();
			
			var map = L.map('map');

			map.setView([41.3887, 2.1777], 13);
			

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
				attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);
		
		map.on('click', function(e){
			console.log(e);
			socket.emit('user_click', e.latlng);
		});

		socket.on('new_user', function(msg){
			console.log(msg);
		});

		</script>
</body>
</html>
```

- Recargar la página. Clicar sobre el mapa y ver las coordenadas del click tanto en el la consola del servidor como en la consola de desarrolladores del navegador.

- Mostrar un marcador en el mapa en la posición donde el usuario hace click. En nuestro html en la función que escucha el evento *new_user* agregar el siguiente código

```html hl_lines="40"
<!DOCTYPE html>
<html>
<head>
	<title>Servicio compartir ubicación realtime</title>
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
		<script src="https://cdn.jsdelivr.net/npm/socket.io-client@4.4.0/dist/socket.io.min.js"></script>
		<script type="text/javascript">
			var socket = io();
			
			var map = L.map('map');

			map.setView([41.3887, 2.1777], 13);
			

		L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
				attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);
		
		map.on('click', function(e){
			console.log(e);
			socket.emit('user_click', e.latlng);
		});

		socket.on('new_user', function(msg){
			console.log(msg);
			L.marker([msg.lat, msg.lng]).addTo(map);
		});

		</script>
</body>
</html>
```

- Recargar nuestra aplicación y abrir otra pestaña con nuestra aplicación para simular que somos dos usuarios distintos. Hacer click en el mapa en cualquiera de las pestañas y ver que nos aparece el marcador en ambas pestañas.

## Referencias

[^1]: https://socket.io/
[^2]: https://es.wikipedia.org/wiki/Socket_de_Internet
[^3]: http://leafletjs.com/
[^4]: https://github.com/domoritz/leaflet-locatecontrol
[^5]: https://nodejs.org/es/
[^6]: http://expressjs.com/
[^7]: https://github.com/socketio/socket.io
[^8]: https://www.npmjs.com/package/cors
[^9]: https://www.npmjs.com/package/nodemon
