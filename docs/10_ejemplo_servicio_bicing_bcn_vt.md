# Bicing con MapLibre: Vector Tiles y datos en tiempo real

En los ejemplos anteriores hemos usado Leaflet para crear mapas web. Aquí veremos otra forma de trabajar con **MapLibre GL JS**: un mapa base servido como Vector Tiles, sobre el que añadiremos las estaciones de Bicing y su disponibilidad actual.

El ejercicio enseña dos fuentes distintas en un mismo mapa:

- el **mapa base** del ICGC, definido mediante un estilo cartográfico que utiliza fuentes vectoriales;
- las **estaciones y su estado**, que consultaremos en dos feeds GBFS y convertiremos a GeoJSON en el navegador.

Las estaciones de Bicing **no** se sirven aquí como Vector Tiles. MapLibre dibuja el mapa base vectorial y permite superponer datos de otros tipos. Esta distinción ayuda a entender que el estilo del mapa, la fuente de datos y la capa que los representa son piezas separadas.

Nos centraremos en el cliente MapLibre y en cómo organiza estilos y capas. La especificación y publicación de Vector Tiles se estudian en la materia de IDES.

**Resultado final:** [abre el visor de Bicing con MapLibre](ejemplos/bicing-maplibre/index.html).

## Qué cambia respecto a Leaflet

Leaflet y MapLibre permiten añadir datos, estilos e interacción. No hay una herramienta que sea mejor para todos los mapas; la elección depende de los datos y del resultado buscado.

| En este ejemplo  | Leaflet                                                             | MapLibre GL JS                                                                                               |
| ---------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Mapa base        | Se suele configurar una capa de teselas y añadirla al mapa.         | Se carga un estilo que describe fuentes y capas cartográficas. Aquí usamos el estilo vectorial del ICGC.     |
| Capa de datos    | Se crean capas, por ejemplo con `L.geoJSON` o marcadores.           | Se declara una fuente con `addSource` y una capa visual con `addLayer`.                                      |
| Estilo por datos | Se configura con opciones o funciones de estilo.                    | Las expresiones permiten variar tamaño y color según atributos o nivel de zoom.                              |
| Renderizado      | Flexible y fácil de empezar; admite distintas capas y complementos. | Utiliza WebGL y está especialmente preparado para estilos basados en datos y mapas vectoriales interactivos. |

En el ejemplo PMR construimos un mapa con Leaflet y marcadores. En este ejemplo observaremos cómo MapLibre mantiene una fuente de datos y modifica el estilo de sus capas sin reconstruir el mapa completo. Las dos bibliotecas pueden mostrar datos GeoJSON; MapLibre también puede representar fuentes vectoriales en el mapa base.

## Datos de Bicing

El [portal Open Data BCN](https://opendata-ajuntament.barcelona.cat/data/es/dataset/informacio-estacions-bicing) publica información del servicio. Para esta demostración usaremos la API de [CityBikes](https://docs.citybik.es/api/gbfs/), que distribuye feeds GBFS de varios sistemas de bicicleta compartida, incluido Bicing. Es un servicio intermediario: si necesitas una fuente oficial para una aplicación operativa, comprueba las condiciones y el acceso que publica Bicing o el Ayuntamiento.

La API ofrece dos feeds separados:

- [`station_information`](https://api.citybik.es/gbfs/2/bicing/station_information.json): identificador, nombre y coordenadas de las estaciones;
- [`station_status`](https://api.citybik.es/gbfs/2/bicing/station_status.json): bicicletas y anclajes disponibles, entre otros datos de estado.

El formato recibido es JSON con una lista de estaciones, no una colección GeoJSON lista para MapLibre. El código unirá ambos feeds usando el identificador de estación y construirá una `FeatureCollection` con puntos. Este feed de información no incluye un campo `capacity`; calcularemos una capacidad estimada sumando las bicicletas y los anclajes disponibles que devuelve el feed de estado. Es una aproximación del total disponible en ese momento, no un aforo fijo de la estación. Solicitaremos el estado cada minuto; esta frecuencia evita hacer peticiones continuas y se puede ajustar según la finalidad y las condiciones de uso del servicio.

## Construir el mapa paso a paso

Crea una carpeta llamada `bicing-maplibre` y dentro un archivo `index.html`. Añadiremos el código por etapas; el archivo completo que puedes copiar y ejecutar está al final de esta sección.

### 1. Crear el mapa base con MapLibre

MapLibre necesita un contenedor y un estilo cartográfico. El estilo del ICGC define las fuentes y capas vectoriales del mapa base; en este paso todavía no aparecen las estaciones.

```html
<div id="map"></div>
```

```js
const map = new maplibregl.Map({
  container: "map",
  style: "https://geoserveis.icgc.cat/contextmaps/icgc.json",
  center: [2.17, 41.39],
  zoom: 12,
});

map.addControl(new maplibregl.NavigationControl(), "top-right");
```

Incluye la hoja de estilos y el archivo JavaScript de MapLibre en el HTML. El contenedor `#map` debe tener alto y ancho definidos para que el mapa sea visible.

### 2. Descargar los dos feeds

La información de las estaciones y su estado se obtiene en peticiones separadas. `Promise.all` espera ambas respuestas; comprobamos los estados HTTP antes de interpretar el JSON:

```js
const responses = await Promise.all([
  fetch(informationUrl),
  fetch(statusUrl),
]);

if (!responses[0].ok || !responses[1].ok) {
  throw new Error("La API no ha podido devolver los dos feeds.");
}

const [information, status] = await Promise.all(
  responses.map((response) => response.json()),
);
```

El bloque debe ejecutarse después de que cargue el mapa. Los datos de estaciones y disponibilidad se reciben como JSON.

### 3. Relacionar estaciones y crear GeoJSON

Los dos feeds comparten el identificador `station_id`. Creamos una tabla para encontrar el estado de cada estación, calculamos una capacidad estimada con las bicis y anclajes disponibles y preparamos una entidad GeoJSON por punto:

```js
const statusById = new Map(
  status.data.stations.map((station) => [station.station_id, station]),
);

const features = information.data.stations.map((station) => {
  const currentStatus = statusById.get(station.station_id);
  const bikes = currentStatus?.num_bikes_available ?? 0;
  const docks = currentStatus?.num_docks_available ?? 0;

  return {
    type: "Feature",
    properties: {
      id: station.station_id,
      name: station.name,
      capacity: bikes + docks,
      bikes,
      docks,
    },
    geometry: {
      type: "Point",
      coordinates: [station.lon, station.lat],
    },
  };
});

const stationsGeoJSON = { type: "FeatureCollection", features };
```

GeoJSON guarda las coordenadas en orden **longitud, latitud**. El campo `capacity` de esta aplicación es una estimación calculada; no viene incluido en el feed de información ni representa necesariamente la capacidad fija de la estación.

### 4. Añadir una fuente y una capa de puntos

MapLibre separa la fuente de datos del estilo de la capa. Añadimos la colección como una fuente GeoJSON y luego declaramos una capa de círculos. El tamaño y el color se basan en atributos de cada estación:

```js
map.addSource("bicing-stations", {
  type: "geojson",
  data: stationsGeoJSON,
});

map.addLayer({
  id: "bicing-points",
  type: "circle",
  source: "bicing-stations",
  paint: {
    "circle-radius": ["interpolate", ["linear"], ["get", "capacity"], 0, 4, 50, 11],
    "circle-color": ["interpolate", ["linear"], ["get", "bikes"], 0, "#d73027", 20, "#1a9850"],
    "circle-stroke-color": "#ffffff",
    "circle-stroke-width": 1,
  },
});
```

Las expresiones `interpolate` definen cómo cambian tamaño y color a medida que cambian los valores. El ejercicio puntuable pide modificar esos rangos.

### 5. Añadir interacción y actualizar los datos

Al pulsar un punto, mostramos el nombre de la estación y los valores actuales. El mapa vuelve a consultar los feeds cada minuto; en las actualizaciones siguientes usa `setData` para cambiar los datos de la fuente existente:

```js
map.on("click", "bicing-points", (event) => {
  const feature = event.features?.[0];
  if (!feature) return;

  const content = document.createElement("div");
  content.textContent =
    `${feature.properties.name}\n` +
    `Bicicletas disponibles: ${feature.properties.bikes}\n` +
    `Anclajes disponibles: ${feature.properties.docks}`;

  new maplibregl.Popup()
    .setLngLat(feature.geometry.coordinates)
    .setDOMContent(content)
    .addTo(map);
});
```

La aplicación también cambia el cursor al pasar sobre una estación. La función completa comprueba si la fuente ya existe para decidir entre crearla por primera vez o actualizarla.

### 6. Ejecutar y probar la aplicación

Guarda los fragmentos en `index.html`. Desde una terminal abierta en la carpeta `bicing-maplibre`, sirve la aplicación localmente:

Desde una terminal abierta en la carpeta `bicing-maplibre`, ejecuta:

```bash
python3 -m http.server 8000
```

Abre `http://localhost:8000` en el navegador. Necesitas conexión a Internet para descargar MapLibre, el estilo del ICGC y los feeds de CityBikes. Al pasar el puntero por una estación cambia el cursor; al hacer clic aparece el número de bicicletas y anclajes disponibles.

## Código completo

Guarda el archivo completo como `index.html`. Este es el mismo código del [visor de Bicing](ejemplos/bicing-maplibre/index.html).

```html
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Disponibilidad de Bicing · MapLibre</title>
    <link
      rel="stylesheet"
      href="https://unpkg.com/maplibre-gl@5.12.0/dist/maplibre-gl.css"
    />
    <style>
      html,
      body,
      #map {
        height: 100%;
        margin: 0;
      }
      #status {
        position: absolute;
        z-index: 1;
        top: 12px;
        left: 12px;
        max-width: min(360px, calc(100% - 48px));
        padding: 8px 10px;
        border-radius: 4px;
        background: white;
        font:
          14px/1.4 system-ui,
          sans-serif;
      }
      .station-popup {
        white-space: pre-line;
      }
    </style>
  </head>
  <body>
    <div id="map"></div>
    <div id="status" role="status">Cargando estaciones…</div>

    <script src="https://unpkg.com/maplibre-gl@5.12.0/dist/maplibre-gl.js"></script>
    <script>
      const map = new maplibregl.Map({
        container: "map",
        style: "https://geoserveis.icgc.cat/contextmaps/icgc.json",
        center: [2.17, 41.39],
        zoom: 12,
      });

      map.addControl(new maplibregl.NavigationControl(), "top-right");

      const informationUrl =
        "https://api.citybik.es/gbfs/2/bicing/station_information.json";
      const statusUrl =
        "https://api.citybik.es/gbfs/2/bicing/station_status.json";
      const statusElement = document.getElementById("status");

      async function updateStations() {
        statusElement.textContent = "Actualizando disponibilidad…";

        try {
          const responses = await Promise.all([
            fetch(informationUrl),
            fetch(statusUrl),
          ]);

          if (!responses[0].ok || !responses[1].ok) {
            throw new Error("La API no ha podido devolver los dos feeds.");
          }

          const [information, status] = await Promise.all(
            responses.map((response) => response.json()),
          );

          const statusById = new Map(
            status.data.stations.map((station) => [
              station.station_id,
              station,
            ]),
          );

          const features = information.data.stations.map((station) => {
            const currentStatus = statusById.get(station.station_id);
            const bikes = currentStatus?.num_bikes_available ?? 0;
            const docks = currentStatus?.num_docks_available ?? 0;

            return {
              type: "Feature",
              properties: {
                id: station.station_id,
                name: station.name,
                capacity: bikes + docks,
                bikes,
                docks,
              },
              geometry: {
                type: "Point",
                coordinates: [station.lon, station.lat],
              },
            };
          });

          const stationsGeoJSON = {
            type: "FeatureCollection",
            features,
          };

          const source = map.getSource("bicing-stations");
          if (source) {
            source.setData(stationsGeoJSON);
          } else {
            map.addSource("bicing-stations", {
              type: "geojson",
              data: stationsGeoJSON,
            });

            map.addLayer({
              id: "bicing-points",
              type: "circle",
              source: "bicing-stations",
              paint: {
                "circle-radius": [
                  "interpolate",
                  ["linear"],
                  ["get", "capacity"],
                  0,
                  4,
                  50,
                  11,
                ],
                "circle-color": [
                  "interpolate",
                  ["linear"],
                  ["get", "bikes"],
                  0,
                  "#d73027",
                  20,
                  "#1a9850",
                ],
                "circle-stroke-color": "#ffffff",
                "circle-stroke-width": 1,
              },
            });

            map.on("click", "bicing-points", (event) => {
              const feature = event.features?.[0];
              if (!feature) return;

              const content = document.createElement("div");
              content.className = "station-popup";
              content.textContent =
                `${feature.properties.name}\n` +
                `Bicicletas disponibles: ${feature.properties.bikes}\n` +
                `Anclajes disponibles: ${feature.properties.docks}`;

              new maplibregl.Popup()
                .setLngLat(feature.geometry.coordinates)
                .setDOMContent(content)
                .addTo(map);
            });

            map.on("mouseenter", "bicing-points", () => {
              map.getCanvas().style.cursor = "pointer";
            });
            map.on("mouseleave", "bicing-points", () => {
              map.getCanvas().style.cursor = "";
            });
          }

          statusElement.textContent = `${features.length} estaciones · actualización cada minuto`;
        } catch (error) {
          console.error(error);
          statusElement.textContent =
            "No se han podido cargar los datos. Revisa la conexión o la consola.";
        }
      }

      map.on("load", () => {
        updateStations();
        window.setInterval(updateStations, 60_000);
      });
    </script>
  </body>
</html>
```

!!! question "Prueba breve en clase · 5–10 minutos"

    Moved el centro del mapa y el nivel de zoom inicial. No hace falta entregar el ejercicio.

## Fuentes, actualización y límites

- La API de CityBikes actúa como intermediaria y puede tener un retraso respecto al servicio oficial. El mapa sirve para explorar disponibilidad; no debe usarse para tomar decisiones operativas sin comprobar los datos y sus condiciones.
- Las coordenadas vienen del feed de información de estaciones; la disponibilidad procede del feed de estado. Se unen por el identificador de estación.
- El mapa base del ICGC incluye su propia atribución. La página indica también que los datos de estaciones proceden de Bicing y llegan mediante CityBikes.
- La frecuencia de actualización del navegador no controla la frecuencia con que el proveedor actualiza los feeds.

## Para ampliar

- [Bicing: mapa oficial de disponibilidad](https://www.bicing.barcelona/es/mapa-de-disponibilidad)
- [Open Data BCN: información de las estaciones](https://opendata-ajuntament.barcelona.cat/data/es/dataset/informacio-estacions-bicing)
- [CityBikes: documentación de su API GBFS (inglés)](https://docs.citybik.es/api/gbfs/)
- [MapLibre GL JS: ejemplos oficiales (inglés)](https://maplibre.org/maplibre-gl-js/docs/examples/)
- [MapLibre GL JS: guía de migración desde Leaflet (inglés)](https://maplibre.org/maplibre-gl-js/docs/guides/leaflet-migration-guide/)
- [MapLibre GL JS: actualizar una fuente GeoJSON (inglés)](https://maplibre.org/maplibre-gl-js/docs/API/classes/GeoJSONSource/)

!!! question "Ejercicio entregable · 2 puntos"

    Modifica el estilo de los puntos de las estaciones y entrega el archivo `index.html` actualizado:

    1. Cambia los valores de la expresión `circle-radius` para ajustar los rangos del tamaño de los puntos según la capacidad estimada de cada estación (1 punto).
    2. Cambia los valores de la expresión `circle-color` para definir un rango de colores distinto según las bicicletas disponibles (1 punto).
