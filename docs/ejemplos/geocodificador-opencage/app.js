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
  address.textContent = result.formatted || "No se encontró una dirección formateada.";
  return address;
}

async function requestOpenCage(parameters) {
  if (!activeApiKey) {
    throw new Error("Introduce tu clave y activa el buscador antes de consultar la API.");
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
    statusElement.textContent = "No se encontraron resultados. Prueba con otra dirección o topónimo.";
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
    if (coordinates.length > 1) map.fitBounds(coordinates, { padding: [24, 24] });
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
  statusElement.textContent = "Buscador activo. Usa el control del mapa, el formulario o haz clic en el mapa.";
});

document.getElementById("search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (query.length < 2) {
    statusElement.textContent = "Escribe al menos dos caracteres para buscar.";
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
      statusElement.textContent = "No se encontró una dirección cercana a ese punto.";
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
