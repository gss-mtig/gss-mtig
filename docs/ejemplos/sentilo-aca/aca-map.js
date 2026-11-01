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
