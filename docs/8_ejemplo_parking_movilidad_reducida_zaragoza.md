# De una API municipal a un mapa: aparcamientos PMR de Zaragoza

En este ejemplo construiremos paso a paso un mapa web con las ubicaciones de aparcamientos reservados a personas con movilidad reducida (PMR) en Zaragoza. La aplicación consultará la API municipal y añadirá un marcador por cada ubicación.

El objetivo es ver cómo unas pocas ideas de programación —variables, una petición, una condición y un bucle— permiten crear un visor que se actualiza con datos del servicio. No hace falta experiencia previa con JavaScript: iremos relacionando cada fragmento con lo que aparece en el mapa.

**Resultado final:** [abre el visor de aparcamientos PMR de Zaragoza](ejemplos/zaragoza-pmr/index.html).

## 1. Conocer los datos y el servicio

El [portal de datos abiertos del Ayuntamiento de Zaragoza](https://www.zaragoza.es/sede/portal/datos-abiertos/) ofrece una API REST con información municipal. En la [documentación interactiva](https://www.zaragoza.es/docs-api_sede/#/Equipamientos%20y%20movilidad%3A%20Aparcamientos%20para%20personas%20con%20discapacidad) se puede encontrar y probar la operación de aparcamientos para personas con discapacidad.

Usaremos una respuesta en formato GeoJSON y solicitaremos coordenadas WGS84 para que el navegador pueda situarlas en el mapa:

```text
https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/equipamiento/aparcamiento-personas-discapacidad.geojson?srsname=wgs84&start=0&rows=50
```

La ficha de [Estacionamientos de personas con discapacidad](https://www.zaragoza.es/web/espacio-de-datos/servicio/catalogo/2720) indica que la información cubre Zaragoza y tiene frecuencia de actualización diaria. La frecuencia publicada no garantiza que cada registro se haya revisado recientemente: conviene comprobar también la fecha y el significado de los datos antes de usarlos.

## 2. Crear el mapa base

Crea una carpeta llamada `visor-aparcamientos-pmr` y, dentro, un archivo `index.html`. Copia este código y ábrelo desde un servidor local, como se explica más abajo. De momento solo aparecerá el mapa base centrado en Zaragoza.

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Aparcamientos PMR de Zaragoza</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    html, body, #map { height: 100%; margin: 0; }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const map = L.map('map').setView([41.65, -0.88], 13);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
  </script>
</body>
</html>
```

`const map` guarda el mapa que crea Leaflet. `setView` fija el centro y el nivel de zoom. La capa de OpenStreetMap proporciona el fondo cartográfico; Leaflet se ocupa de dibujar y permitir la interacción con el mapa.

## 3. Consultar la API

Ahora añadiremos la consulta al final del mismo bloque `<script>`, después de crear el mapa base:

```js
const url = 'https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/equipamiento/aparcamiento-personas-discapacidad.geojson?srsname=wgs84&start=0&rows=50';

fetch(url)
  .then(response => response.json())
  .then(data => {
    console.log(data);
  })
  .catch(error => console.error('No se pudieron cargar los datos:', error));
```

`url` es una variable con la dirección del servicio. `fetch(url)` hace la petición; las funciones `then` continúan el proceso cuando llega la respuesta. `response.json()` interpreta el contenido como datos que JavaScript puede manejar. `console.log(data)` permite inspeccionar la respuesta en la consola del navegador (F12 → **Consola**).

Este patrón es asíncrono: el navegador puede seguir mostrando el mapa mientras espera los datos. `catch` permite mostrar en la consola un error si falla la consulta o la respuesta.

## 4. Recorrer los resultados y añadir marcadores

En la consola, abre `features` y observa un registro. Cada elemento contiene una geometría y unas propiedades. En una geometría de tipo `Point`, las coordenadas aparecen en orden **longitud, latitud**. Leaflet, en cambio, recibe las posiciones como **latitud, longitud**; por eso las asignaremos en ese orden al crear cada marcador.

Reemplaza `console.log(data);` por este fragmento:

```js
data.features.forEach(feature => {
  if (!feature.geometry || feature.geometry.type !== 'Point') return;

  const [longitud, latitud] = feature.geometry.coordinates;
  const propiedades = feature.properties;

  const marker = L.marker([latitud, longitud]).addTo(map);
  marker.bindPopup(
    `<strong>${propiedades.tipo_reserva || 'Aparcamiento PMR'}</strong><br>
     Dirección: ${propiedades.calle_1 || 'No disponible'}, ${propiedades.num_calle1 || 's/n'}<br>
     Plazas: ${propiedades.plazas ?? 'No disponible'}`
  );
});
```

`forEach` repite las instrucciones para cada elemento de `features`. La condición `if` omite registros que no tengan un punto. El bucle crea un marcador y una ventana emergente para cada ubicación. Si algún campo no está informado, se muestra un texto alternativo.

## 5. Código completo

Este es el archivo completo con los pasos anteriores. Puedes copiarlo si quieres probar el ejemplo por tu cuenta:

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Aparcamientos PMR de Zaragoza</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    html, body, #map { height: 100%; margin: 0; }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const map = L.map('map').setView([41.65, -0.88], 13);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const url = 'https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/equipamiento/aparcamiento-personas-discapacidad.geojson?srsname=wgs84&start=0&rows=50';

    fetch(url)
      .then(response => response.json())
      .then(data => {
        data.features.forEach(feature => {
          if (!feature.geometry || feature.geometry.type !== 'Point') return;

          const [longitud, latitud] = feature.geometry.coordinates;
          const propiedades = feature.properties;

          const marker = L.marker([latitud, longitud]).addTo(map);
          marker.bindPopup(
            `<strong>${propiedades.tipo_reserva || 'Aparcamiento PMR'}</strong><br>
             Dirección: ${propiedades.calle_1 || 'No disponible'}, ${propiedades.num_calle1 || 's/n'}<br>
             Plazas: ${propiedades.plazas ?? 'No disponible'}`
          );
        });
      })
      .catch(error => console.error('No se pudieron cargar los datos:', error));
  </script>
</body>
</html>
```

### Ejecutar el archivo

Algunas funciones del navegador pueden restringir las peticiones a una API si se abre el archivo directamente con `file://`. Para servirlo localmente, abre una terminal en la carpeta `visor-aparcamientos-pmr` y ejecuta:

```bash
python3 -m http.server 8000
```

Después abre `http://localhost:8000` en el navegador. Si no tienes Python instalado, puedes usar cualquier servidor local para archivos web. Si el mapa base aparece pero no los marcadores, revisa la consola: puede haber cambiado el servicio o su configuración de acceso.

!!! question "Pausa para comprobar · 5 minutos"

    Antes de ejecutar el código completo, predecid qué ocurrirá si intercambiamos `longitud` y `latitud` en `L.marker`. Después probadlo y comparad el resultado. ¿Qué aporta el `if` dentro del bucle?

## Práctica opcional en casa

Si quieres seguir practicando, elige una ampliación:

- cambia el centro o el zoom inicial del mapa;
- muestra en la ventana emergente otro atributo disponible;
- cambia `rows=50` para solicitar más o menos registros y observa el resultado;
- cambia el marcador por un círculo de Leaflet y modifica su tamaño o color.

La ampliación es voluntaria y no se entrega. Antes de compartir un mapa, revisa la atribución de la cartografía base y las condiciones de reutilización de los datos.

## Referencias

- [API REST del Ayuntamiento de Zaragoza](https://www.zaragoza.es/sede/portal/datos-abiertos/api)
- [Documentación interactiva de aparcamientos para personas con discapacidad](https://www.zaragoza.es/docs-api_sede/#/Equipamientos%20y%20movilidad%3A%20Aparcamientos%20para%20personas%20con%20discapacidad)
- [Ficha del conjunto y atributos disponibles](https://www.zaragoza.es/web/espacio-de-datos/servicio/catalogo/2720)
- [Leaflet: guía de inicio (inglés)](https://leafletjs.com/examples/quick-start/)
