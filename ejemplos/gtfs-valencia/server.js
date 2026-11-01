const path = require("node:path");
const express = require("express");
const JSZip = require("jszip");
const { parse } = require("csv-parse/sync");

const FEED_URL = process.env.GTFS_URL ||
  "https://opendata.vlci.valencia.es/dataset/ab058cf8-ad3e-4d9c-ac89-0c6367ecf351/resource/c81b69e6-c082-44dc-acc6-66fc417b4e66/download/google_transit.zip";
const PORT = Number(process.env.PORT || 3000);
const app = express();

async function leerTabla(zip, nombre) {
  const archivo = Object.values(zip.files).find((entrada) =>
    !entrada.dir && entrada.name.split("/").pop() === nombre
  );
  if (!archivo) throw new Error(`El feed GTFS no contiene ${nombre}`);

  const texto = await archivo.async("string");
  return parse(texto, {
    bom: true,
    columns: true,
    skip_empty_lines: true
  });
}

function crearGeoJSON(paradas, puntosForma) {
  const featuresParadas = paradas.flatMap((parada) => {
    const lat = Number(parada.stop_lat);
    const lon = Number(parada.stop_lon);
    if (!parada.stop_id || !Number.isFinite(lat) || !Number.isFinite(lon)) return [];
    return [{
      type: "Feature",
      id: parada.stop_id,
      properties: {
        stop_id: parada.stop_id,
        stop_name: parada.stop_name || "Parada sin nombre"
      },
      geometry: { type: "Point", coordinates: [lon, lat] }
    }];
  });

  const grupos = new Map();
  puntosForma.forEach((punto) => {
    const lat = Number(punto.shape_pt_lat);
    const lon = Number(punto.shape_pt_lon);
    if (!punto.shape_id || !Number.isFinite(lat) || !Number.isFinite(lon)) return;
    if (!grupos.has(punto.shape_id)) grupos.set(punto.shape_id, []);
    grupos.get(punto.shape_id).push({
      secuencia: Number(punto.shape_pt_sequence),
      coordenada: [lon, lat]
    });
  });

  const featuresLineas = [...grupos.entries()].flatMap(([shapeId, puntos]) => {
    puntos.sort((a, b) => a.secuencia - b.secuencia);
    if (puntos.length < 2) return [];
    return [{
      type: "Feature",
      id: shapeId,
      properties: { shape_id: shapeId },
      geometry: {
        type: "LineString",
        coordinates: puntos.map((punto) => punto.coordenada)
      }
    }];
  });

  return {
    paradas: { type: "FeatureCollection", features: featuresParadas },
    lineas: { type: "FeatureCollection", features: featuresLineas }
  };
}

async function cargarFeed() {
  const respuesta = await fetch(FEED_URL, { signal: AbortSignal.timeout(30_000) });
  if (!respuesta.ok) throw new Error(`El portal GTFS respondió HTTP ${respuesta.status}`);
  const zip = await JSZip.loadAsync(await respuesta.arrayBuffer());
  const [paradas, puntosForma] = await Promise.all([
    leerTabla(zip, "stops.txt"),
    leerTabla(zip, "shapes.txt")
  ]);
  return crearGeoJSON(paradas, puntosForma);
}

app.use(express.static(path.join(__dirname, "public")));

let datosGTFS;
app.get("/api/stops", (req, res) => {
  if (!datosGTFS) return res.status(503).json({ error: "El feed todavía se está cargando" });
  res.json(datosGTFS.paradas);
});
app.get("/api/shapes", (req, res) => {
  if (!datosGTFS) return res.status(503).json({ error: "El feed todavía se está cargando" });
  res.json(datosGTFS.lineas);
});

cargarFeed()
  .then((datos) => {
    datosGTFS = datos;
    app.listen(PORT, () => {
      console.log(`Visor GTFS listo en http://localhost:${PORT}`);
      console.log(`${datos.paradas.features.length} paradas y ${datos.lineas.features.length} recorridos cargados`);
    });
  })
  .catch((error) => {
    console.error(`No se pudo cargar el feed GTFS: ${error.message}`);
    process.exitCode = 1;
  });
