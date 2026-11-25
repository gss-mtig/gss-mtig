# Consultar puntos de recarga eléctrica con OpenStreetMap

**Resultado final:** [abre el visor de puntos de recarga eléctrica](ejemplos/overpass-recarga/index.html).

En esta práctica consultaremos puntos de recarga de vehículos eléctricos registrados en OpenStreetMap y los mostraremos en un mapa. Usaremos **Overpass API**, un geoservicio que permite buscar elementos de OpenStreetMap por sus etiquetas y por la zona seleccionada. No hace falta instalar programas ni escribir una consulta desde cero: el visor prepara la consulta al pulsar el botón.

Los datos describen lo que está registrado en OpenStreetMap. No indican si un cargador está libre, funciona en este momento o está disponible para cualquier persona. La información sobre conectores y acceso también puede faltar.

## 1. Probar el visor

Abre el [visor de puntos de recarga](ejemplos/overpass-recarga/index.html). Acerca el mapa a una zona que conozcas y pulsa **Buscar en esta zona**. La consulta se hace solo cuando pulsas el botón, para no enviar peticiones continuamente mientras mueves el mapa.

Pulsa un marcador para ver el nombre, los conectores y la información de acceso cuando estén registrados. Si no aparecen resultados, prueba otra zona más amplia o inténtalo más tarde: el servicio público puede estar ocupado.

## 2. Qué servicio estamos consultando

Overpass API permite pedir elementos de OpenStreetMap que cumplen unas condiciones. Para localizar puntos de recarga, buscamos la etiqueta `amenity=charging_station`. Una etiqueta es un par formado por una clave y un valor; en este caso, `amenity` indica el tipo de lugar y `charging_station` identifica una estación de recarga.

La consulta limita la búsqueda al rectángulo visible del mapa. Así se solicita solo una parte del territorio en lugar de descargar datos de toda la ciudad. El servicio puede devolver puntos (`node`) o elementos con geometría de área (`way` y `relation`). En el segundo caso, pedimos al servicio un punto central para poder colocarlos como marcadores.

```text
[out:json][timeout:25];
(
  node["amenity"="charging_station"](sur,oeste,norte,este);
  way["amenity"="charging_station"](sur,oeste,norte,este);
  relation["amenity"="charging_station"](sur,oeste,norte,este);
);
out center tags;
```

Los valores `sur,oeste,norte,este` los calcula el visor usando los límites actuales del mapa. `out center tags` pide las etiquetas y, para las áreas, una coordenada central.

## 3. Mostrar resultados en Leaflet

El navegador envía la consulta mediante una petición `POST`. Overpass devuelve un objeto JSON con una lista llamada `elements`. Cada elemento tiene etiquetas en `tags`; los puntos incluyen latitud y longitud, mientras que las áreas incluyen `center`.

La función siguiente escoge las coordenadas que existan. Para las etiquetas no construimos HTML a partir de los datos: insertamos el texto con `textContent`, de modo que nombres externos se muestren como texto.

```js
function elementPosition(element) {
  if (element.type === "node") return [element.lat, element.lon];
  if (element.center) return [element.center.lat, element.center.lon];
  return null;
}

for (const element of data.elements) {
  const position = elementPosition(element);
  if (!position || !element.tags) continue;

  L.circleMarker(position, {
    radius: 7,
    fillColor: "#1976a5",
  })
    .bindPopup(makePopup(element.tags))
    .addTo(resultsLayer);
}
```

La aplicación completa también comprueba si la respuesta tiene la estructura esperada, muestra errores HTTP y deja volver a intentar si el servicio no responde. La fecha de actualización incluida por Overpass se muestra en el panel; la frecuencia de consulta no significa que OpenStreetMap se actualice a ese mismo ritmo.

## 4. Código completo

Guarda el código siguiente como `index.html` y ábrelo con un servidor local sencillo, por ejemplo la extensión Live Server de Visual Studio Code. También puedes usar directamente el visor enlazado al principio. El ejemplo no necesita un servidor propio ni una clave de API.

```html
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Puntos de recarga eléctrica</title>
    <link
      rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    />
    <style>
      html,
      body,
      #map {
        height: 100%;
        margin: 0;
      }
      body {
        font-family: system-ui, sans-serif;
      }
      #panel {
        position: absolute;
        z-index: 1000;
        top: 12px;
        left: 60px;
        max-width: min(360px, calc(100vw - 100px));
        padding: 10px 12px;
        border-radius: 6px;
        background: #fff;
        box-shadow: 0 1px 5px #5558;
      }
      #panel p {
        margin: 6px 0;
      }
      #buscar {
        min-height: 2.5rem;
        padding: 6px 12px;
        border: 0;
        border-radius: 4px;
        color: #fff;
        background: #1457a6;
        font: inherit;
        cursor: pointer;
      }
      #buscar:disabled {
        opacity: 0.6;
        cursor: wait;
      }
      #estado {
        font-size: 0.9rem;
      }
    </style>
  </head>
  <body>
    <div id="panel">
      <strong>Puntos de recarga eléctrica</strong>
      <p>Acerca o aleja el mapa y pulsa el botón para consultar esa zona.</p>
      <button id="buscar" type="button">Buscar en esta zona</button>
      <p id="estado" role="status" aria-live="polite">
        Elige una zona del mapa para empezar.
      </p>
    </div>
    <div id="map" aria-label="Mapa de puntos de recarga eléctrica"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const OVERPASS_URL = "https://overpass-api.de/api/interpreter";
      const map = L.map("map").setView([41.3874, 2.1686], 13);
      const resultsLayer = L.layerGroup().addTo(map);
      const button = document.querySelector("#buscar");
      const status = document.querySelector("#estado");

      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
      }).addTo(map);

      function makePopup(tags) {
        const content = document.createElement("div");
        const title = document.createElement("strong");
        title.textContent = tags.name || "Punto de recarga sin nombre";
        content.append(title);

        const connectors = Object.entries(tags)
          .filter(([key]) => key.startsWith("socket:") && !key.endsWith(":output"))
          .map(([key, value]) => `${key.replace("socket:", "")} : ${value}`);
        const details = [
          connectors.length
            ? `Conectores: ${connectors.join(", ")}`
            : "Conectores: no indicados",
          `Acceso: ${tags.access || "no indicado"}`,
        ];

        for (const detail of details) {
          const line = document.createElement("div");
          line.textContent = detail;
          content.append(line);
        }
        return content;
      }

      function elementPosition(element) {
        if (element.type === "node") return [element.lat, element.lon];
        if (element.center) return [element.center.lat, element.center.lon];
        return null;
      }

      async function searchVisibleArea() {
        const bounds = map.getBounds();
        const bbox = [
          bounds.getSouth(),
          bounds.getWest(),
          bounds.getNorth(),
          bounds.getEast(),
        ].join(",");
        const query = `[out:json][timeout:25];(node["amenity"="charging_station"](${bbox});way["amenity"="charging_station"](${bbox});relation["amenity"="charging_station"](${bbox}););out center tags;`;

        button.disabled = true;
        resultsLayer.clearLayers();
        status.textContent = "Consultando OpenStreetMap…";

        try {
          const response = await fetch(OVERPASS_URL, {
            method: "POST",
            body: new URLSearchParams({ data: query }),
          });
          if (!response.ok) {
            throw new Error(`El servicio respondió HTTP ${response.status}.`);
          }

          const data = await response.json();
          if (data.remark) throw new Error(data.remark);
          if (!Array.isArray(data.elements)) {
            throw new Error("La respuesta no contiene una lista de resultados.");
          }

          let count = 0;
          for (const element of data.elements) {
            const position = elementPosition(element);
            if (!position || !element.tags) continue;
            L.circleMarker(position, {
              radius: 7,
              color: "#ffffff",
              weight: 2,
              fillColor: "#1976a5",
              fillOpacity: 0.9,
            })
              .bindPopup(makePopup(element.tags))
              .addTo(resultsLayer);
            count += 1;
          }

          const timestamp = data.osm3s?.timestamp_osm_base;
          status.textContent = timestamp
            ? `${count} puntos · datos OSM consultados: ${timestamp}`
            : `${count} puntos encontrados en esta zona.`;
        } catch (error) {
          status.textContent = `No se pudieron consultar los datos. Espera un momento y vuelve a intentarlo. (${error.message})`;
        } finally {
          button.disabled = false;
        }
      }

      button.addEventListener("click", searchVisibleArea);
    </script>
  </body>
</html>
```

## Actividad breve en clase (5 minutos)

En parejas, consultad dos zonas distintas del mapa. Comparad cuántos resultados aparecen y qué información falta en algunos popups. Comentad por qué no se puede interpretar la ausencia de un punto como prueba de que no exista un cargador en la realidad. No hace falta entregar la actividad.

## Fuentes, límites y atribución

- [Overpass API: documentación oficial](https://dev.overpass-api.de/overpass-doc/en/)
- [OpenStreetMap: etiqueta de estación de recarga](https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dcharging_station)
- [Política de uso de la instancia pública Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API#Public_Overpass_API_instances)
- [OpenStreetMap: derechos de autor y atribución](https://www.openstreetmap.org/copyright)

La instancia pública puede responder lentamente o rechazar consultas cuando está ocupada. Haz una sola consulta cada vez y espera antes de reintentar. La cobertura depende de las aportaciones a OpenStreetMap; los resultados no sustituyen una fuente oficial para localizar o comprobar la disponibilidad operativa de cargadores.

## Ejercicio entregable

!!! question "Ampliar la ficha de un punto de recarga — 2 puntos"

    Modifica la función `makePopup` para añadir estos datos de la estación:

    1. Muestra el operador (`operator`) (0,5 puntos).
    2. Muestra la potencia máxima de toda la estación (`charging_station:output`), con su unidad si está incluida en el dato (0,5 puntos).
    3. Muestra la capacidad (`capacity`): el número total de vehículos que pueden cargarse al mismo tiempo (0,5 puntos).
    4. Para cada campo que no esté presente, muestra **«no indicado»** en lugar de dejarlo vacío (0,5 puntos).

    Usa `textContent`, como en el código de la práctica, para mostrar los valores. `capacity` no es necesariamente el número de conectores: indica cuántos vehículos pueden cargarse simultáneamente. Este dato es opcional y puede no estar registrado en OpenStreetMap.

    **Entrega:** el archivo `index.html` actualizado y una captura de un popup donde se vean los tres campos. Si falta alguno en la estación elegida, la captura debe mostrar **«no indicado»**. No hace falta entregar una copia de los datos ni crear una consulta nueva.

    **Criterios:** operador visible (0,5 puntos); potencia visible (0,5 puntos); capacidad visible con el significado correcto (0,5 puntos); texto alternativo para los campos ausentes (0,5 puntos).

**Fin del recorrido:** [volver al temario](index.md).
