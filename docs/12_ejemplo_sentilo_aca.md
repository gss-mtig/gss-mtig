# Consumo de sensores de la ACA con Sentilo

En esta práctica construiremos un mapa web con las ubicaciones de los embalses de Cataluña y mostraremos las últimas medidas al seleccionar un embalse. La Agencia Catalana del Agua (ACA) publica estos datos mediante su API REST basada en Sentilo.

**Resultado final:** [abre el ejemplo de Sentilo ACA](ejemplos/sentilo-aca/index.html).

La página ofrece una vista de referencia y, al ejecutarla en local, consulta la API actual.

!!! note "Calidad y actualización de los datos"

    La ACA indica que las medidas en tiempo real no están revisadas ni validadas y pueden contener errores. Úsalas para explorar el servicio; antes de tomar decisiones, comprueba el valor, la unidad, la fecha y la calidad de la medida.

## 1. Entender la API y sus identificadores

La API ofrece dos consultas que usaremos:

1. El [catálogo de embalses](https://aplicacions.aca.gencat.cat/sdim2/apirest/catalog?componentType=embassament) describe las estaciones y las variables de sus sensores. Cada entrada incluye, entre otros campos, `provider`, `sensor`, `component`, `componentDesc`, `location` y `unit`.
2. La consulta de [últimas medidas](https://aplicacions.aca.gencat.cat/sdim2/apirest/data/EMBASSAMENT-EST/083036-001-ANA023) usa el proveedor y el **identificador de la variable**. La respuesta incluye una lista `observations` con el valor y la marca de tiempo.

La respuesta del catálogo es JSON, no GeoJSON. Además, `location` contiene dos números como texto en orden **latitud, longitud**. Para GeoJSON debemos convertirlos y guardarlos como **longitud, latitud**. Un embalse puede tener varias variables de sensor; las agruparemos por el identificador `component` para dibujar un único punto por estación y consultar cada variable al abrir su ficha.

El endpoint de medidas documentado por la ACA es `GET /sdim2/apirest/data/{provider}/{sensor}`. En el resto de esta práctica usamos esta API en lugar de la antigua ruta del visor web `lastOb`.

## 2. Preparar y ejecutar el ejemplo

Instala [Node.js](https://nodejs.org/es/) versión 18 o posterior. Crea una carpeta `visor-aca` y copia dentro los cuatro archivos del [ejemplo descargable](ejemplos/sentilo-aca/archivos.md): `server.js`, `index.html`, `aca-data.js` y `aca-map.js`.

Abre una terminal en `visor-aca` e instala Express:

```bash
npm init -y
npm install express
```

El servidor local entrega la página y consulta la API de la ACA. El navegador solo habla con `localhost`, así que no necesita hacer peticiones entre dominios. Desde la misma carpeta, arranca el servidor:

```bash
node server.js
```

Abre [http://localhost:3000](http://localhost:3000). Necesitas conexión a Internet para cargar el mapa base de OpenStreetMap y consultar los datos de la ACA.

## 3. Servidor local y acceso a la API

`server.js` publica dos rutas locales: `/api/catalog` para las estaciones y `/api/data/{provider}/{sensor}` para consultar una variable. Comprueba los identificadores antes de construir la petición y reenvía al navegador la respuesta de la ACA.

### Código de `server.js`

```js
const express = require("express");

const app = express();
const port = process.env.PORT || 3000;
const acaApi = "https://aplicacions.aca.gencat.cat/sdim2/apirest";

app.use(express.static(__dirname));

app.get("/api/catalog", async (_request, response) => {
  await forwardJson(
    `${acaApi}/catalog?componentType=embassament`,
    response,
  );
});

app.get("/api/data/:provider/:sensor", async (request, response) => {
  const { provider, sensor } = request.params;
  const validId = /^[A-Za-z0-9_-]+$/;

  if (!validId.test(provider) || !validId.test(sensor)) {
    response.status(400).json({ error: "Identificador no válido." });
    return;
  }

  const url = `${acaApi}/data/${encodeURIComponent(provider)}/${encodeURIComponent(sensor)}`;
  await forwardJson(url, response);
});

async function forwardJson(url, response) {
  try {
    const acaResponse = await fetch(url, {
      headers: { Accept: "application/json" },
    });
    const body = await acaResponse.text();
    const contentType = acaResponse.headers.get("content-type");

    response.status(acaResponse.status);
    if (contentType) response.set("content-type", contentType);
    response.send(body);
  } catch (error) {
    console.error("No se pudo consultar la API de la ACA:", error);
    response.status(502).json({ error: "No se pudo consultar la API de la ACA." });
  }
}

app.listen(port, () => {
  console.log(`Visor disponible en http://localhost:${port}`);
});
```

Express define rutas con `app.get`. El servidor usa `fetch`, disponible en Node.js 18 y versiones posteriores, para consultar la ACA. El catálogo es una consulta más lenta y menos volátil que las medidas; el navegador lo carga una vez al iniciar el mapa y solo consulta medidas cuando se selecciona un embalse.

## 4. Transformar el catálogo en GeoJSON

`aca-data.js` busca el proveedor por su identificador, valida las coordenadas y agrupa las variables por embalse. La función se puede probar de forma independiente y también la utiliza el mapa.

### Código de `aca-data.js`

```js
function catalogToGeoJSON(catalog) {
  const provider = catalog?.providers?.find(
    (item) => item.provider === "EMBASSAMENT-EST",
  );

  if (!provider) {
    throw new Error("El catálogo no contiene el proveedor EMBASSAMENT-EST.");
  }

  const stations = new Map();

  for (const sensor of provider.sensors || []) {
    const coordinates = String(sensor.location || "")
      .trim()
      .split(/\s+/)
      .map(Number);
    const [latitude, longitude] = coordinates;
    const component = sensor.component;

    if (
      coordinates.length !== 2 ||
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude) ||
      latitude < 40 || latitude > 43 ||
      longitude < 0 || longitude > 4 ||
      !component ||
      !sensor.sensor
    ) {
      continue;
    }

    if (!stations.has(component)) {
      stations.set(component, {
        type: "Feature",
        properties: {
          provider: provider.provider,
          component,
          name: sensor.componentDesc || component,
          sensors: [],
        },
        geometry: {
          type: "Point",
          coordinates: [longitude, latitude],
        },
      });
    }

    stations.get(component).properties.sensors.push({
      id: sensor.sensor,
      description: sensor.description || sensor.type || "Medida",
      unit: sensor.unit || "",
    });
  }

  return {
    type: "FeatureCollection",
    features: Array.from(stations.values()),
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { catalogToGeoJSON };
} else {
  window.AcaSentilo = { catalogToGeoJSON };
}
```

En el catálogo, `component` identifica la estación y `sensor` identifica una variable medida. Por eso el mapa crea una entidad GeoJSON por componente, pero conserva todos los identificadores de sensor para poder pedir sus medidas por separado. El módulo exporta la función para poder comprobar la transformación con Node.js.

## 5. Dibujar los embalses y consultar sus medidas

El archivo `index.html` prepara el mapa y carga los dos scripts. `aca-map.js` consulta el catálogo, dibuja un círculo por estación y, al hacer clic, solicita las últimas medidas de sus sensores.

### Código de `index.html`

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Embalses de Cataluña · datos de la ACA</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    html, body { height: 100%; margin: 0; font: 16px/1.4 system-ui, sans-serif; }
    #map { height: 100%; }
    #status {
      position: absolute;
      z-index: 1000;
      top: 12px;
      left: 12px;
      max-width: min(390px, calc(100% - 48px));
      padding: 10px 12px;
      border-radius: 5px;
      background: white;
      box-shadow: 0 1px 5px #5558;
    }
    #preview { display: none; max-width: 100%; }
    #preview img { display: block; width: min(100%, 900px); height: auto; }
  </style>
</head>
<body>
  <div id="status" role="status">Cargando los datos de los embalses…</div>
  <div id="map"></div>
  <figure id="preview">
    <img src="preview.png" alt="Vista de referencia del mapa de embalses de Cataluña">
    <figcaption>Vista de referencia. Para cargar medidas actuales, ejecuta el servidor local descrito en la lección.</figcaption>
  </figure>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="aca-data.js"></script>
  <script src="aca-map.js"></script>
</body>
</html>
```

### Código de `aca-map.js`

```js
const map = L.map("map").setView([41.65, 1.5], 8);
const statusElement = document.getElementById("status");
const previewElement = document.getElementById("preview");

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Error HTTP ${response.status}`);
  return response.json();
}

async function loadStations() {
  try {
    const catalog = await getJson("/api/catalog");
    const geojson = AcaSentilo.catalogToGeoJSON(catalog);

    if (geojson.features.length === 0) {
      throw new Error("El catálogo no contiene embalses con coordenadas válidas.");
    }

    const layer = L.geoJSON(geojson, {
      pointToLayer: (_feature, latlng) => L.circleMarker(latlng, {
        radius: 7,
        color: "#155e9a",
        weight: 2,
        fillColor: "#3b9ddd",
        fillOpacity: 0.85,
      }),
      onEachFeature: (feature, marker) => {
        marker.on("click", () => showStationReadings(feature, marker));
      },
    }).addTo(map);

    map.fitBounds(layer.getBounds().pad(0.12));
    statusElement.textContent = `${geojson.features.length} embalses cargados. Selecciona un punto para consultar las medidas.`;
    previewElement.style.display = "none";
  } catch (error) {
    console.error(error);
    statusElement.textContent = "La vista publicada muestra una captura de referencia. Para consultar la API, ejecuta server.js localmente.";
    map.getContainer().style.display = "none";
    previewElement.style.display = "block";
  }
}

async function showStationReadings(feature, marker) {
  const popup = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = feature.properties.name;
  popup.append(title);

  const message = document.createElement("p");
  message.textContent = "Consultando las últimas medidas…";
  popup.append(message);
  marker.bindPopup(popup).openPopup();

  const readings = await Promise.allSettled(
    feature.properties.sensors.map(async (sensor) => {
      const provider = encodeURIComponent(feature.properties.provider);
      const sensorId = encodeURIComponent(sensor.id);
      const data = await getJson(`/api/data/${provider}/${sensorId}`);
      return { sensor, observation: data.observations?.[0] };
    }),
  );

  message.remove();
  const list = document.createElement("ul");

  for (const result of readings) {
    const item = document.createElement("li");
    if (result.status === "rejected") {
      item.textContent = "No se pudo consultar una de las variables.";
    } else {
      const { sensor, observation } = result.value;
      item.textContent = observation
        ? `${sensor.description}: ${observation.value} ${sensor.unit} · ${observation.timestamp}`
        : `${sensor.description}: no hay una medida disponible.`;
    }
    list.append(item);
  }

  popup.append(list);
}

loadStations();
```

El mapa solo dibuja ubicaciones válidas. En la ficha, `Promise.allSettled` permite mostrar las variables disponibles aunque falle una consulta individual. El texto del popup se construye con `textContent`, y la fecha y unidad ayudan a interpretar cada valor.

!!! question "Prueba breve en clase · 5–10 minutos"

    Abrid la ficha de un embalse y buscad qué campos describen la variable, su unidad y el momento de observación. Después, cambiad el color o el tamaño de los círculos. No hace falta entregar esta prueba.

## Referencias

- [Datos abiertos en tiempo real de la ACA (catalán)](https://aca.gencat.cat/ca/laigua/consulta-de-dades/dades-obertes/dades-obertes-temps-real/)
- [Manual de la API REST de la ACA (catalán)](https://aca.gencat.cat/web/.content/20_Aigua/08_consulta_de_dades/01_dades_obertes/02_dades_obertes_temps_real/us_serveis_dades_API_REST.pdf)
- [Mapa oficial de sensores de la ACA](https://aplicacions.aca.gencat.cat/sentilo-catalog-web/component/map)
- [Sentilo en el Centro de Transferencia de Tecnología de la Administración española](https://administracionelectronica.gob.es/ctt/sentilo)
- [Documentación oficial de la API Sentilo (inglés)](https://sentilo.readthedocs.io/en/latest/api_docs.html)
- [Leaflet: guía de inicio (inglés)](https://leafletjs.com/examples/quick-start/)
