# Geocodificación con OpenCage

La **geocodificación directa** convierte una dirección o un topónimo en coordenadas. La **geocodificación inversa** usa coordenadas para encontrar la dirección o el lugar más cercano. El resultado es aproximado: un geocodificador puede devolver varias coincidencias y no sustituye la comprobación de la dirección.

En esta práctica construiremos un mapa web con Leaflet y el [control de geocodificación de OpenCage](https://github.com/OpenCageData/leaflet-opencage-geocoding). El alumnado podrá comparar ese control con un formulario propio que consulta la API mediante `fetch`. Al hacer clic en el mapa, consultaremos la dirección más cercana.

**Resultado final:** [abre la aplicación de OpenCage](ejemplos/geocodificador-opencage/index.html).

Para probar consultas, introduce tu propia clave API. Los archivos [index.html](ejemplos/geocodificador-opencage/index.html) y [app.js](ejemplos/geocodificador-opencage/app.js) contienen el código completo.

## Preparar el ejemplo

1. Crea una cuenta en [OpenCage](https://opencagedata.com/) y genera una clave de prueba personal. La API requiere una clave para cada petición.
2. Descarga [index.html](ejemplos/geocodificador-opencage/index.html) y [app.js](ejemplos/geocodificador-opencage/app.js), y guárdalos juntos en una carpeta local.
3. Desde esa carpeta, inicia un servidor web local:

   ```bash
   python3 -m http.server 8000
   ```

4. Abre [http://localhost:8000](http://localhost:8000), introduce tu clave y pulsa **Activar buscador**. Prueba tanto el control de búsqueda que aparece sobre el mapa como el formulario **Búsqueda directa con fetch**. Haz clic en el mapa para probar la geocodificación inversa.

La página no contiene una clave preconfigurada ni la guarda: la introduces en el campo mientras haces la práctica. La clave se envía en cada petición a OpenCage y puede verse en las herramientas de desarrollo del navegador. Usa tu propia clave de prueba; no copies una clave compartida en el código ni la publiques en un repositorio. Para una aplicación pública real, las credenciales deben gestionarse desde un servidor.

## Entender la petición y la respuesta

El control de Leaflet realiza la búsqueda directa internamente. El formulario propio muestra cómo construir una URL, añadir los parámetros y procesar la respuesta con `fetch`. Para la consulta inversa, el código envía `q` con latitud y longitud en ese orden. La respuesta incluye `results`; cada resultado tiene una dirección formateada y coordenadas `geometry.lat` y `geometry.lng`. El popup inicial muestra únicamente la dirección. El ejercicio pide ampliarlo con otros campos de la respuesta.

La API puede devolver varias coincidencias. El campo `confidence` es una indicación de precisión del resultado, no una probabilidad de que la dirección sea correcta ni un criterio para ordenar las coincidencias. Revisa el contexto y las alternativas antes de elegir.

## Construir la aplicación paso a paso

Crea `index.html` y `app.js` en la misma carpeta. Primero montaremos el mapa, después activaremos el control de OpenCage con una clave introducida en el navegador y, por último, haremos nuestras propias peticiones para la búsqueda directa e inversa.

### 1. Crear el mapa y preparar sus capas

El HTML reserva una columna para el formulario y otra para el mapa. En `app.js`, Leaflet crea el mapa y dos grupos separados para que las búsquedas directas e inversas puedan actualizar sus resultados sin mezclarlos:

```js
const map = L.map("map").setView([41.387, 2.17], 13);
const forwardMarkers = L.featureGroup().addTo(map);
const reverseMarker = L.featureGroup().addTo(map);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
  maxZoom: 19,
}).addTo(map);
```

### 2. Activar el control de búsqueda

La persona introduce su propia clave y pulsa **Activar buscador**. El control de Leaflet recibe esa clave y consulta OpenCage cuando se escribe una dirección en el mapa:

```js
activeApiKey = keyInput.value.trim();
geocodingControl = L.Control.openCageGeocoding({
  key: activeApiKey,
  limit: 5,
  position: "topright",
  placeholder: "Buscar dirección o lugar…",
  collapsed: false,
}).addTo(map);
```

El control se carga con los archivos CSS y JavaScript del plugin. La clave solo se mantiene en la página abierta y no está escrita en el código del ejemplo.

### 3. Consultar la API con `fetch`

El formulario propio permite observar cómo se construye la petición. `URLSearchParams` codifica la dirección y los parámetros; la respuesta JSON se comprueba antes de devolver la lista `results`:

```js
const url = new URL(apiEndpoint);
Object.entries({
  key: activeApiKey,
  language: "es",
  countrycode: "es",
  ...parameters,
}).forEach(([name, value]) => url.searchParams.set(name, value));

const response = await fetch(url);
const data = await response.json();
if (!response.ok || data.status?.code !== 200) {
  throw new Error(data.status?.message || `Error HTTP ${response.status}`);
}
return data.results || [];
```

La búsqueda directa manda el texto introducido y representa las coincidencias válidas como marcadores. El código inicial muestra su dirección formateada en los popups.

### 4. Consultar una dirección desde el mapa

Al hacer clic, usamos la latitud y la longitud del punto como consulta inversa. El popup muestra solo la dirección; el ejercicio puntuable pide ampliarlo con otros atributos de la respuesta:

```js
const query = `${event.latlng.lat},${event.latlng.lng}`;
const results = await requestOpenCage({ q: query });
const result = results[0];

const marker = L.marker([result.geometry.lat, result.geometry.lng])
  .bindPopup(makePopupContent(result))
  .addTo(reverseMarker);
marker.openPopup();
```

`makePopupContent` crea el contenido del popup usando únicamente `result.formatted`. Así queda una aplicación funcional de partida sin incluir la solución del ejercicio de ampliación.

### Código de `index.html`

```html
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Geocodificación con OpenCage</title>
    <link
      rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    />
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.1.0/dist/css/L.Control.OpenCageGeocoding.min.css"
    />
    <style>
      * {
        box-sizing: border-box;
      }
      html,
      body {
        height: 100%;
        margin: 0;
        font:
          16px/1.45 system-ui,
          sans-serif;
      }
      #app {
        display: grid;
        grid-template-columns: minmax(320px, 380px) minmax(0, 1fr);
        grid-template-rows: minmax(0, 1fr);
        width: 100%;
        height: 100vh;
      }
      aside {
        grid-column: 1;
        grid-row: 1;
        min-width: 0;
        overflow: auto;
        padding: 1rem;
        border-right: 1px solid #d1d5db;
      }
      h1 {
        margin-top: 0;
        font-size: 1.4rem;
      }
      label {
        display: block;
        margin: 1rem 0 0.3rem;
        font-weight: 600;
      }
      input,
      button {
        width: 100%;
        padding: 0.65rem;
        font: inherit;
      }
      button {
        cursor: pointer;
      }
      form button {
        margin-top: 0.6rem;
      }
      #status {
        min-height: 3rem;
        padding: 0.5rem 0;
      }
      #results {
        padding-left: 1.5rem;
      }
      #results li {
        margin: 0.5rem 0;
      }
      #results button {
        text-align: left;
        border: 1px solid #d1d5db;
        border-radius: 0.3rem;
        background: #fff;
      }
      #results button:hover {
        background: #f3f4f6;
      }
      #map {
        grid-column: 2;
        grid-row: 1;
        min-width: 0;
        min-height: 0;
        height: 100vh;
      }
      .note {
        font-size: 0.9rem;
        color: #374151;
      }
      @media (max-width: 700px) {
        #app {
          grid-template-columns: minmax(0, 1fr);
          grid-template-rows: minmax(320px, 55vh) auto;
          height: auto;
          min-height: 100vh;
        }
        aside {
          grid-column: 1;
          grid-row: 2;
          border-right: 0;
          border-top: 1px solid #d1d5db;
        }
        #map {
          grid-column: 1;
          grid-row: 1;
          height: 55vh;
          min-height: 320px;
          max-height: 520px;
        }
      }
    </style>
  </head>
  <body>
    <main id="app">
      <aside>
        <h1>Geocodificador OpenCage</h1>
        <p>
          Compara dos formas de buscar: el control de OpenCage sobre el mapa y
          una petición propia a la API desde este formulario. Haz clic en el
          mapa para probar la búsqueda inversa.
        </p>
        <form id="key-form">
          <label for="api-key">Tu clave API de OpenCage</label>
          <input
            id="api-key"
            type="password"
            autocomplete="off"
            placeholder="Pega tu clave para esta sesión"
            required
          />
          <button type="submit">Activar buscador</button>
        </form>
        <form id="search-form">
          <label for="query">Búsqueda directa mediante petición a la API</label>
          <input id="query" value="Plaça de Catalunya, Barcelona" required />
          <button type="submit">Consultar la API</button>
        </form>
        <p class="note">
          La clave solo se mantiene en esta página mientras está abierta. No la
          guardes en el código ni compartas una clave personal en una web
          pública.
        </p>
        <div id="status" role="status" aria-live="polite">
          Introduce tu clave para añadir el control de búsqueda al mapa.
        </div>
        <ol id="results"></ol>
      </aside>
      <div id="map" aria-label="Mapa interactivo"></div>
    </main>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@v2.1.0/dist/js/L.Control.OpenCageGeocoding.min.js"></script>
    <script src="app.js"></script>
  </body>
</html>
```

### Código de `app.js`

```js
const apiEndpoint = "https://api.opencagedata.com/geocode/v1/json";
const map = L.map("map").setView([41.387, 2.17], 13);
const keyInput = document.getElementById("api-key");
const queryInput = document.getElementById("query");
const statusElement = document.getElementById("status");
const resultsElement = document.getElementById("results");
const forwardMarkers = L.featureGroup().addTo(map);
const reverseMarker = L.featureGroup().addTo(map);
let activeApiKey = "";
let geocodingControl = null;

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
  maxZoom: 19,
}).addTo(map);

function makePopupContent(result) {
  const address = document.createElement("div");
  address.textContent =
    result.formatted || "No se encontró una dirección formateada.";
  return address;
}

async function requestOpenCage(parameters) {
  if (!activeApiKey) {
    throw new Error(
      "Introduce tu clave y activa el buscador antes de consultar la API.",
    );
  }

  const url = new URL(apiEndpoint);
  Object.entries({
    key: activeApiKey,
    language: "es",
    countrycode: "es",
    ...parameters,
  }).forEach(([name, value]) => url.searchParams.set(name, value));

  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok || data.status?.code !== 200) {
    throw new Error(data.status?.message || `Error HTTP ${response.status}`);
  }
  return data.results || [];
}

function showForwardResults(results) {
  resultsElement.replaceChildren();
  forwardMarkers.clearLayers();

  if (results.length === 0) {
    statusElement.textContent =
      "No se encontraron resultados. Prueba con otra dirección o topónimo.";
    return;
  }

  const coordinates = [];
  results.forEach((result, index) => {
    const latitude = Number(result.geometry?.lat);
    const longitude = Number(result.geometry?.lng);
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return;

    const marker = L.marker([latitude, longitude])
      .bindPopup(makePopupContent(result))
      .addTo(forwardMarkers);
    coordinates.push([latitude, longitude]);

    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = result.formatted || `Resultado ${index + 1}`;
    button.addEventListener("click", () => {
      map.setView([latitude, longitude], 16);
      marker.openPopup();
    });
    item.append(button);
    resultsElement.append(item);
  });

  if (coordinates.length === 0) {
    statusElement.textContent = "La respuesta no contiene coordenadas válidas.";
  } else {
    statusElement.textContent = `${coordinates.length} resultado(s) encontrados con fetch.`;
    if (coordinates.length === 1) map.setView(coordinates[0], 16);
    if (coordinates.length > 1)
      map.fitBounds(coordinates, { padding: [24, 24] });
  }
}

document.getElementById("key-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const key = keyInput.value.trim();
  if (!key) {
    statusElement.textContent = "Introduce una clave API de OpenCage.";
    return;
  }

  activeApiKey = key;
  if (geocodingControl) map.removeControl(geocodingControl);
  geocodingControl = L.Control.openCageGeocoding({
    key: activeApiKey,
    limit: 5,
    position: "topright",
    placeholder: "Buscar dirección o lugar…",
    errorMessage: "No se encontraron resultados.",
    collapsed: false,
  }).addTo(map);
  statusElement.textContent =
    "Buscador activo. Usa el control del mapa, el formulario o haz clic en el mapa.";
});

document
  .getElementById("search-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = queryInput.value.trim();
    if (query.length < 2) {
      statusElement.textContent =
        "Escribe al menos dos caracteres para buscar.";
      return;
    }

    statusElement.textContent = "Consultando la API con fetch…";
    try {
      const results = await requestOpenCage({ q: query, limit: "5" });
      showForwardResults(results);
    } catch (error) {
      statusElement.textContent = error.message;
    }
  });

map.on("click", async (event) => {
  statusElement.textContent = "Consultando la dirección más cercana…";
  try {
    const query = `${event.latlng.lat},${event.latlng.lng}`;
    const results = await requestOpenCage({ q: query });
    const result = results[0];
    if (!result) {
      statusElement.textContent =
        "No se encontró una dirección cercana a ese punto.";
      return;
    }

    const latitude = Number(result.geometry?.lat);
    const longitude = Number(result.geometry?.lng);
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
      throw new Error("La respuesta no contiene coordenadas válidas.");
    }

    reverseMarker.clearLayers();
    const marker = L.marker([latitude, longitude])
      .bindPopup(makePopupContent(result))
      .addTo(reverseMarker);
    map.setView([latitude, longitude], 16);
    marker.openPopup();
    statusElement.textContent = "Dirección cercana encontrada.";
  } catch (error) {
    statusElement.textContent = error.message;
  }
});
```

!!! question "Prueba breve en clase · 5–10 minutos"

    Busca **Plaça de Catalunya, Barcelona** con el control del mapa y luego con el formulario. Compara cómo se inicia cada búsqueda y qué resultados aparecen. Después, haz clic en otra zona del mapa para consultar la dirección más cercana.

## Ejercicio entregable

!!! question "Ampliar la información del popup de OpenCage — 1 punto"

    En el popup de la búsqueda inversa, muestra la confianza (`confidence`), la categoría (`_category`) y el tipo (`_type`). Si alguno de esos campos no está presente, indícalo sin dejar el popup vacío ni provocar un error.

    **Entrega:** el archivo `index.html` actualizado y una captura de un popup de búsqueda inversa con esos atributos. No incluyas la clave de API en el archivo ni en la captura.

    **Criterio:** se muestran los tres atributos y la aplicación gestiona los campos ausentes (1 punto).

## Geocodificador del ICGC (opcional)

Para practicar con un servicio público centrado en Cataluña, consulta el [ejemplo opcional del Geocodificador ICGC](15_ejemplo_geocodificador_icgc.md). Incluye la aplicación completa y realiza búsqueda directa e inversa.

## Referencias

- [OpenCage: documentación de la API (inglés)](https://opencagedata.com/api)
- [OpenCage: control de geocodificación para Leaflet (inglés)](https://github.com/OpenCageData/leaflet-opencage-geocoding)
- [OpenCage: página de cuenta y claves](https://opencagedata.com/)
- [Leaflet: referencia de la API (inglés)](https://leafletjs.com/reference.html)

**Siguiente:** [Geocodificador ICGC (opcional)](15_ejemplo_geocodificador_icgc.md).
