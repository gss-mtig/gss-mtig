const map = L.map("map").setView([39.4652, -0.3861], 12);
const estado = document.querySelector("#estado");

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap contributors</a>",
  maxZoom: 19
}).addTo(map);
map.attributionControl.addAttribution(
  '<a href="https://opendata.vlci.valencia.es/dataset/google-transit-lines-stops-bus-schedules">Datos EMT València</a> · <a href="https://creativecommons.org/licenses/by/4.0/deed.es">CC BY 4.0</a>'
);

function colorDeLinea(shapeId) {
  let hash = 0;
  for (const caracter of shapeId) hash = (hash * 31 + caracter.charCodeAt(0)) >>> 0;
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
  if (!respuesta.ok) throw new Error(`Error HTTP ${respuesta.status} al consultar ${url}`);
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
      cargarGeoJSON(window.GTFS_URLS.paradas)
    ]);

    const lineas = L.geoJSON(datosLineas, {
      style: (feature) => ({
        color: colorDeLinea(String(feature.properties?.shape_id || "ruta")),
        weight: 3,
        opacity: 0.75
      })
    }).addTo(map);

    const paradas = L.geoJSON(datosParadas, {
      pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
        radius: 4,
        fillColor: "#a30000",
        color: "#ffffff",
        weight: 1,
        fillOpacity: 0.9
      }),
      onEachFeature: (feature, layer) => layer.bindPopup(popupParada(feature.properties || {}))
    }).addTo(map);

    const bounds = L.featureGroup([lineas, paradas]).getBounds();
    if (bounds.isValid()) map.fitBounds(bounds.pad(0.04));
    estado.textContent = `${datosLineas.features.length} recorridos y ${datosParadas.features.length} paradas · feed GTFS estático`;
  } catch (error) {
    estado.textContent = `No se pudieron cargar los datos: ${error.message}`;
  }
}

iniciarVisor();
