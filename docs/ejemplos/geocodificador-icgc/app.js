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
