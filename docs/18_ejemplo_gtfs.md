# 🚌 Ejemplo: representar un feed GTFS en un mapa

**Resultado final:** [abre la vista previa del mapa de EMT València](ejemplos/gtfs-valencia/index.html). La vista previa usa una copia estática reducida del feed para dibujar más rápido; la aplicación local desarrollada en esta página descarga el feed publicado por EMT València al iniciarse.

En esta práctica convertiremos dos tablas de un feed GTFS en GeoJSON y las mostraremos con Leaflet: las paradas de `stops.txt` y los recorridos descritos en `shapes.txt`. Para leer el archivo ZIP usaremos Node.js en un servidor local. El servidor evita depender de que el navegador permita descargar directamente el ZIP desde el portal y entrega al mapa respuestas GeoJSON sencillas.

## 1. GTFS estático y GTFS en tiempo real

GTFS (General Transit Feed Specification) es una especificación abierta para publicar información de transporte público. Un feed **GTFS Schedule** o estático suele ser un archivo ZIP con tablas CSV: rutas, paradas, viajes, calendarios, horarios y, a menudo, geometrías de los recorridos. Las tablas se relacionan mediante identificadores como `route_id`, `trip_id`, `stop_id` y `shape_id`.

GTFS estático describe el servicio planificado. **GTFS Realtime** es otra especificación para comunicar cambios del servicio, alertas y posiciones de vehículos. La página anterior muestra un servicio de posiciones en tiempo real de FGC; aquí trabajamos con horarios y geometrías planificadas.

Consulta la [referencia oficial de GTFS Schedule en español](https://gtfs.org/es/documentation/schedule/reference/) y el [conjunto GTFS de EMT València](https://opendata.vlci.valencia.es/dataset/google-transit-lines-stops-bus-schedules). El portal publica el feed como ZIP bajo licencia CC BY 4.0. La URL directa utilizada por el ejemplo está en el código del servidor y puede cambiar si el portal reorganiza el recurso.

## 2. Crear el mapa base

Crea una carpeta llamada `visor-gtfs` con esta estructura. El proyecto incluye el servidor y los archivos del mapa:

```text
visor-gtfs/
├── package.json
├── server.js
└── public/
    ├── index.html
    ├── app.js
    └── style.css
```

El HTML carga Leaflet y el código de la aplicación. El objeto `GTFS_URLS` indica al mapa qué direcciones consultar; el servidor local ofrece las rutas `/api/stops` y `/api/shapes`.

```html
<div id="estado" role="status">Cargando feed GTFS…</div>
<div id="map" aria-label="Mapa de paradas y recorridos de EMT València"></div>
<script>
  window.GTFS_URLS = { paradas: "/api/stops", lineas: "/api/shapes" };
</script>
```

## 3. Preparar Node.js y las dependencias

Instala [Node.js (versión 18 o posterior)](https://nodejs.org/es/). En la carpeta del proyecto ejecuta:

```bash
npm install
npm start
```

El proyecto usa Express para el servidor, JSZip para abrir el feed ZIP y `csv-parse` para leer las tablas CSV. Son dependencias declaradas en `package.json`; no hace falta instalar herramientas globales como `nodemon`.

## 4. Descargar el ZIP y leer las tablas GTFS

El servidor descarga el feed una vez al iniciarse. Después abre el ZIP en memoria y busca `stops.txt` y `shapes.txt`, aunque el proveedor los haya colocado dentro de una carpeta. El parser CSV reconoce campos entre comillas y los encabezados de las tablas.

```js
async function leerTabla(zip, nombre) {
  const archivo = Object.values(zip.files).find(
    (entrada) => !entrada.dir && entrada.name.split("/").pop() === nombre,
  );
  if (!archivo) throw new Error(`El feed GTFS no contiene ${nombre}`);

  const texto = await archivo.async("string");
  return parse(texto, {
    bom: true,
    columns: true,
    skip_empty_lines: true,
  });
}
```

## 5. Convertir paradas y recorridos a GeoJSON

Cada fila válida de `stops.txt` se convierte en un punto GeoJSON. GTFS almacena primero longitud y luego latitud al crear las coordenadas GeoJSON: `[stop_lon, stop_lat]`.

En `shapes.txt`, varias filas con el mismo `shape_id` forman una línea. Las ordenamos por `shape_pt_sequence` antes de construir la geometría `LineString`. Así, el mapa dibuja cada recorrido en el orden correcto.

```js
const grupos = new Map();
puntosForma.forEach((punto) => {
  if (!grupos.has(punto.shape_id)) grupos.set(punto.shape_id, []);
  grupos.get(punto.shape_id).push({
    secuencia: Number(punto.shape_pt_sequence),
    coordenada: [Number(punto.shape_pt_lon), Number(punto.shape_pt_lat)],
  });
});

const featuresLineas = [...grupos.entries()].map(([shapeId, puntos]) => {
  puntos.sort((a, b) => a.secuencia - b.secuencia);
  return {
    type: "Feature",
    properties: { shape_id: shapeId },
    geometry: {
      type: "LineString",
      coordinates: puntos.map((punto) => punto.coordenada),
    },
  };
});
```

El código completo también descarta coordenadas no numéricas y geometrías con menos de dos puntos.

## 6. Publicar los GeoJSON desde el servidor

Una vez convertidas las tablas, Express las devuelve desde dos rutas. La página del mapa consume estas rutas con `fetch` y dibuja las respuestas mediante `L.geoJSON`.

```js
app.get("/api/stops", (req, res) => {
  res.json(datosGTFS.paradas);
});

app.get("/api/shapes", (req, res) => {
  res.json(datosGTFS.lineas);
});
```

Al abrir `http://localhost:3000` se muestran las paradas y los recorridos. Puedes pulsar una parada para ver su nombre y código. Los colores de los recorridos ayudan a distinguir geometrías; se asignan en el navegador para esta demostración y no representan necesariamente el color oficial de cada línea.

> **Atribución:** los datos de transporte proceden de EMT València / Ajuntament de València y se publican con licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). La cartografía base es de OpenStreetMap.

## Actividad breve en clase (5–10 minutos)

🟦 **Explora las tablas**

Abre el conjunto de EMT València y localiza `stops.txt`, `shapes.txt` y `trips.txt`. ¿Qué identificador permite agrupar los puntos que forman una geometría? ¿Por qué no se puede deducir el horario de paso de un autobús solo mirando `shapes.txt`?

## Código completo

Los siguientes archivos forman el proyecto ejecutable. Guarda cada bloque con el nombre que indica el encabezado.

### `package.json`

```json
{
  "name": "visor-gtfs-valencia",
  "version": "1.0.0",
  "private": true,
  "description": "Visor didáctico de datos GTFS de EMT València",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "engines": {
    "node": ">=18"
  },
  "dependencies": {
    "csv-parse": "7.0.3",
    "express": "5.3.0",
    "jszip": "3.10.2"
  }
}
```

### `server.js`

```js
const path = require("node:path");
const express = require("express");
const JSZip = require("jszip");
const { parse } = require("csv-parse/sync");

const FEED_URL =
  process.env.GTFS_URL ||
  "https://opendata.vlci.valencia.es/dataset/ab058cf8-ad3e-4d9c-ac89-0c6367ecf351/resource/c81b69e6-c082-44dc-acc6-66fc417b4e66/download/google_transit.zip";
const PORT = Number(process.env.PORT || 3000);
const app = express();

async function leerTabla(zip, nombre) {
  const archivo = Object.values(zip.files).find(
    (entrada) => !entrada.dir && entrada.name.split("/").pop() === nombre,
  );
  if (!archivo) throw new Error(`El feed GTFS no contiene ${nombre}`);

  const texto = await archivo.async("string");
  return parse(texto, {
    bom: true,
    columns: true,
    skip_empty_lines: true,
  });
}

function crearGeoJSON(paradas, puntosForma) {
  const featuresParadas = paradas.flatMap((parada) => {
    const lat = Number(parada.stop_lat);
    const lon = Number(parada.stop_lon);
    if (!parada.stop_id || !Number.isFinite(lat) || !Number.isFinite(lon))
      return [];
    return [
      {
        type: "Feature",
        id: parada.stop_id,
        properties: {
          stop_id: parada.stop_id,
          stop_name: parada.stop_name || "Parada sin nombre",
        },
        geometry: { type: "Point", coordinates: [lon, lat] },
      },
    ];
  });

  const grupos = new Map();
  puntosForma.forEach((punto) => {
    const lat = Number(punto.shape_pt_lat);
    const lon = Number(punto.shape_pt_lon);
    if (!punto.shape_id || !Number.isFinite(lat) || !Number.isFinite(lon))
      return;
    if (!grupos.has(punto.shape_id)) grupos.set(punto.shape_id, []);
    grupos.get(punto.shape_id).push({
      secuencia: Number(punto.shape_pt_sequence),
      coordenada: [lon, lat],
    });
  });

  const featuresLineas = [...grupos.entries()].flatMap(([shapeId, puntos]) => {
    puntos.sort((a, b) => a.secuencia - b.secuencia);
    if (puntos.length < 2) return [];
    return [
      {
        type: "Feature",
        id: shapeId,
        properties: { shape_id: shapeId },
        geometry: {
          type: "LineString",
          coordinates: puntos.map((punto) => punto.coordenada),
        },
      },
    ];
  });

  return {
    paradas: { type: "FeatureCollection", features: featuresParadas },
    lineas: { type: "FeatureCollection", features: featuresLineas },
  };
}

async function cargarFeed() {
  const respuesta = await fetch(FEED_URL, {
    signal: AbortSignal.timeout(30_000),
  });
  if (!respuesta.ok)
    throw new Error(`El portal GTFS respondió HTTP ${respuesta.status}`);
  const zip = await JSZip.loadAsync(await respuesta.arrayBuffer());
  const [paradas, puntosForma] = await Promise.all([
    leerTabla(zip, "stops.txt"),
    leerTabla(zip, "shapes.txt"),
  ]);
  return crearGeoJSON(paradas, puntosForma);
}

app.use(express.static(path.join(__dirname, "public")));

let datosGTFS;
app.get("/api/stops", (req, res) => {
  if (!datosGTFS)
    return res.status(503).json({ error: "El feed todavía se está cargando" });
  res.json(datosGTFS.paradas);
});
app.get("/api/shapes", (req, res) => {
  if (!datosGTFS)
    return res.status(503).json({ error: "El feed todavía se está cargando" });
  res.json(datosGTFS.lineas);
});

cargarFeed()
  .then((datos) => {
    datosGTFS = datos;
    app.listen(PORT, () => {
      console.log(`Visor GTFS listo en http://localhost:${PORT}`);
      console.log(
        `${datos.paradas.features.length} paradas y ${datos.lineas.features.length} recorridos cargados`,
      );
    });
  })
  .catch((error) => {
    console.error(`No se pudo cargar el feed GTFS: ${error.message}`);
    process.exitCode = 1;
  });
```

### `public/index.html`

```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Visor GTFS de EMT València</title>
    <link
      rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    />
    <link rel="stylesheet" href="style.css" />
  </head>
  <body>
    <div id="estado" role="status">Cargando feed GTFS…</div>
    <div
      id="map"
      aria-label="Mapa de paradas y recorridos de EMT València"
    ></div>
    <script>
      window.GTFS_URLS = { paradas: "/api/stops", lineas: "/api/shapes" };
    </script>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="app.js"></script>
  </body>
</html>
```

### `public/app.js`

```js
const map = L.map("map").setView([39.4652, -0.3861], 12);
const estado = document.querySelector("#estado");

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
  maxZoom: 19,
}).addTo(map);
map.attributionControl.addAttribution(
  '<a href="https://opendata.vlci.valencia.es/dataset/google-transit-lines-stops-bus-schedules">Datos EMT València</a> · <a href="https://creativecommons.org/licenses/by/4.0/deed.es">CC BY 4.0</a>',
);

function colorDeLinea(shapeId) {
  let hash = 0;
  for (const caracter of shapeId)
    hash = (hash * 31 + caracter.charCodeAt(0)) >>> 0;
  return `hsl(${hash % 360} 72% 42%)`;
}

function popupParada(datos) {
  const contenido = document.createElement("div");
  const nombre = document.createElement("strong");
  nombre.textContent = datos.stop_name || "Parada sin nombre";
  const id = document.createElement("div");
  id.textContent = `Código: ${datos.stop_id || "No disponible"}`;
  contenido.append(nombre, id);
  return contenido;
}

async function cargarGeoJSON(url) {
  const respuesta = await fetch(url);
  if (!respuesta.ok)
    throw new Error(`Error HTTP ${respuesta.status} al consultar ${url}`);
  const datos = await respuesta.json();
  if (datos.type !== "FeatureCollection" || !Array.isArray(datos.features)) {
    throw new Error(`La respuesta de ${url} no tiene estructura GeoJSON`);
  }
  return datos;
}

async function iniciarVisor() {
  try {
    const [datosLineas, datosParadas] = await Promise.all([
      cargarGeoJSON(window.GTFS_URLS.lineas),
      cargarGeoJSON(window.GTFS_URLS.paradas),
    ]);

    const lineas = L.geoJSON(datosLineas, {
      style: (feature) => ({
        color: colorDeLinea(String(feature.properties?.shape_id || "ruta")),
        weight: 3,
        opacity: 0.75,
      }),
    }).addTo(map);

    const paradas = L.geoJSON(datosParadas, {
      pointToLayer: (feature, latlng) =>
        L.circleMarker(latlng, {
          radius: 4,
          fillColor: "#a30000",
          color: "#ffffff",
          weight: 1,
          fillOpacity: 0.9,
        }),
      onEachFeature: (feature, layer) =>
        layer.bindPopup(popupParada(feature.properties || {})),
    }).addTo(map);

    const bounds = L.featureGroup([lineas, paradas]).getBounds();
    if (bounds.isValid()) map.fitBounds(bounds.pad(0.04));
    estado.textContent = `${datosLineas.features.length} recorridos y ${datosParadas.features.length} paradas · feed GTFS estático`;
  } catch (error) {
    estado.textContent = `No se pudieron cargar los datos: ${error.message}`;
  }
}

iniciarVisor();
```

### `public/style.css`

```css
html,
body,
#map {
  height: 100%;
  margin: 0;
}
body {
  font-family: system-ui, sans-serif;
}
#estado {
  position: absolute;
  z-index: 1000;
  top: 12px;
  left: 60px;
  max-width: min(520px, calc(100vw - 100px));
  padding: 9px 12px;
  border-radius: 6px;
  background: #fff;
  box-shadow: 0 1px 5px #5558;
  font-size: 14px;
}
```

!!! exercise "Ejercicio entregable · 2,5 puntos"

    1. Carga en el visor el feed GTFS estático de [FGC](https://dadesobertes.fgc.cat/explore/assets/gtfs_zip/?flg=es-es) y centra el mapa en Cataluña para que se vea la red (1 punto).
    2. Añade un popup a las líneas que muestre el valor de `shape_id` (0,5 puntos).
    3. Añade al mapa los trenes en tiempo real de FGC (1 punto).

    El código de la práctica termina antes de estos cambios: tendrás que investigar el feed y completar las tres tareas. Puedes consultar el [ejemplo anterior de posiciones FGC en tiempo real](19_ejemplo_fgc_realtime.md) como referencia para el tercer apartado.
