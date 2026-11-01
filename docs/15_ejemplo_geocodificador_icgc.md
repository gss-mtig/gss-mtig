# Geocodificador ICGC (opcional)

Este ejemplo opcional permite comparar OpenCage con un servicio público especializado en direcciones y topónimos de Cataluña. El [Geocodificador ICGC](https://www.icgc.cat/es/Herramientas-y-visores/Herramientas/Geocodificador-ICGC) expone operaciones REST para búsqueda directa, autocompletado y búsqueda inversa. Aquí usaremos búsqueda directa y búsqueda inversa.

**Resultado final:** [abre la aplicación del ICGC](ejemplos/geocodificador-icgc/index.html).

La aplicación no necesita una clave API. Descarga [index.html](ejemplos/geocodificador-icgc/index.html) y [app.js](ejemplos/geocodificador-icgc/app.js), guárdalos juntos y ejecuta un servidor local:

```bash
python3 -m http.server 8000
```

Después abre [http://localhost:8000](http://localhost:8000). La búsqueda directa consulta `/cerca` con el texto, las capas y el número máximo de resultados; al hacer clic en el mapa se consulta `/invers` con latitud y longitud. Ambas operaciones devuelven GeoJSON en orden de coordenadas longitud-latitud; Leaflet interpreta ese orden al cargar una entidad GeoJSON.

## Código completo

### Código de `index.html`

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Geocodificador ICGC</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    * { box-sizing: border-box; }
    html, body { height: 100%; margin: 0; font: 16px/1.45 system-ui, sans-serif; }
    #app { display: grid; grid-template-columns: minmax(280px, 360px) 1fr; height: 100%; }
    aside { overflow: auto; padding: 1rem; border-right: 1px solid #d1d5db; }
    h1 { margin-top: 0; font-size: 1.4rem; }
    label { display: block; margin: 1rem 0 .3rem; font-weight: 600; }
    input, button { width: 100%; padding: .65rem; font: inherit; }
    button { cursor: pointer; }
    form button { margin-top: .6rem; }
    #status { min-height: 3rem; padding: .5rem 0; }
    #results { padding-left: 1.5rem; }
    #results li { margin: .5rem 0; }
    #results button { text-align: left; border: 1px solid #d1d5db; border-radius: .3rem; background: #fff; }
    #results button:hover { background: #f3f4f6; }
    #map { min-height: 360px; }
    @media (max-width: 700px) {
      #app { grid-template-columns: 1fr; grid-template-rows: minmax(260px, 42vh) 1fr; }
      aside { grid-row: 2; border-right: 0; border-top: 1px solid #d1d5db; }
      #map { grid-row: 1; }
    }
  </style>
</head>
<body>
  <main id="app">
    <aside>
      <h1>Geocodificador ICGC</h1>
      <p>Busca direcciones y topónimos de Cataluña. Haz clic en el mapa para localizar el elemento más cercano.</p>
      <form id="search-form">
        <label for="query">Dirección o topónimo</label>
        <input id="query" value="Plaça de Catalunya, Barcelona" required>
        <button type="submit">Buscar</button>
      </form>
      <div id="status" role="status" aria-live="polite">Escribe una dirección o un topónimo para comenzar.</div>
      <ol id="results"></ol>
    </aside>
    <div id="map" aria-label="Mapa interactivo"></div>
  </main>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="app.js"></script>
</body>
</html>
```

### Código de `app.js`

```js
const serviceUrl = "https://eines.icgc.cat/geocodificador";
const map = L.map("map").setView([41.65, 1.7], 8);
const queryInput = document.getElementById("query");
const statusElement = document.getElementById("status");
const resultsElement = document.getElementById("results");
const resultLayer = L.geoJSON(null, {
  pointToLayer: (_feature, latlng) => L.marker(latlng),
}).addTo(map);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
  maxZoom: 19,
}).addTo(map);

async function requestFeatures(operation, parameters) {
  const url = new URL(`${serviceUrl}/${operation}`);
  Object.entries(parameters).forEach(([name, value]) => url.searchParams.set(name, value));

  const response = await fetch(url);
  if (!response.ok) throw new Error(`Error HTTP ${response.status} al consultar el ICGC.`);
  const data = await response.json();
  if (data.type !== "FeatureCollection" || !Array.isArray(data.features)) {
    throw new Error("La respuesta del ICGC no tiene la estructura GeoJSON esperada.");
  }
  return data.features;
}

function featureLabel(feature) {
  const properties = feature.properties || {};
  return properties.etiqueta || properties.label || properties.nom || "Resultado del ICGC";
}

function showFeatures(features, emptyMessage) {
  resultsElement.replaceChildren();
  resultLayer.clearLayers();

  if (features.length === 0) {
    statusElement.textContent = emptyMessage;
    return;
  }

  const validFeatures = features.filter((feature) =>
    feature.geometry?.type === "Point" &&
    Array.isArray(feature.geometry.coordinates) &&
    feature.geometry.coordinates.length >= 2 &&
    feature.geometry.coordinates.every(Number.isFinite),
  );
  if (validFeatures.length === 0) {
    statusElement.textContent = "La respuesta no contiene puntos con coordenadas válidas.";
    return;
  }

  resultLayer.addData({ type: "FeatureCollection", features: validFeatures });
  resultLayer.eachLayer((layer) => {
    const feature = layer.feature;
    const label = featureLabel(feature);
    const popup = document.createElement("div");
    popup.textContent = label;
    layer.bindPopup(popup);

    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", () => {
      map.setView(layer.getLatLng(), 16);
      layer.openPopup();
    });
    item.append(button);
    resultsElement.append(item);
  });

  statusElement.textContent = `${validFeatures.length} resultado(s). Selecciona uno para centrar el mapa.`;
  if (validFeatures.length === 1) map.fitBounds(resultLayer.getBounds().pad(0.2));
  else map.fitBounds(resultLayer.getBounds(), { padding: [24, 24] });
}

document.getElementById("search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = queryInput.value.trim();
  if (text.length < 2) {
    statusElement.textContent = "Escribe al menos dos caracteres para buscar.";
    return;
  }

  statusElement.textContent = "Buscando en el ICGC…";
  try {
    const features = await requestFeatures("cerca", {
      text,
      layers: "address,topo1,topo2",
      size: "5",
    });
    showFeatures(features, "No se encontraron resultados. Prueba con otra dirección o topónimo de Cataluña.");
  } catch (error) {
    statusElement.textContent = error.message;
  }
});

map.on("click", async (event) => {
  statusElement.textContent = "Buscando la dirección o el topónimo más cercano…";
  try {
    const features = await requestFeatures("invers", {
      lat: String(event.latlng.lat),
      lon: String(event.latlng.lng),
      layers: "address,topo1,topo2",
      size: "1",
    });
    showFeatures(features, "No se encontraron direcciones ni topónimos próximos a ese punto.");
  } catch (error) {
    statusElement.textContent = error.message;
  }
});
```

!!! question "Prueba opcional · 5–10 minutos"

    Busca una dirección con municipio, por ejemplo **Carrer Nou 10, Girona**, y después haz clic en el mapa. Compara el formato y los atributos de la respuesta con OpenCage. Comprueba que GeoJSON almacena las coordenadas como longitud-latitud aunque Leaflet muestre los marcadores en el lugar correcto.

!!! exercise "Ejercicio entregable · 2 puntos"

    Modifica la aplicación y entrega los archivos `index.html` y `app.js`:

    1. Muestra la propiedad `layer` del resultado junto con la etiqueta o dirección en el popup (1 punto).
    2. En la búsqueda inversa, representa los tres primeros resultados como marcadores y abre automáticamente solo el popup del primero (1 punto).

## Referencias

- [Geocodificador ICGC: información en español](https://www.icgc.cat/es/Herramientas-y-visores/Herramientas/Geocodificador-ICGC)
- [Documentación del Geocodificador ICGC en español](https://openicgc.github.io/geocodificador-doc_es/)
- [Parámetros de búsqueda directa](https://openicgc.github.io/geocodificador-doc_es/parametres_cerca.es/)
- [Parámetros de búsqueda inversa](https://openicgc.github.io/geocodificador-doc_es/parametres_invers.es/)
- [Leaflet: referencia de la API (inglés)](https://leafletjs.com/reference.html)
