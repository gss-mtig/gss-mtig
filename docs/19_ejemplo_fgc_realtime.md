# 🚆 Trenes de FGC en tiempo real

**Resultado final:** [abre el mapa de trenes de FGC](ejemplos/fgc-trenes-realtime/index.html). El visor consulta las API públicas de FGC desde el navegador y muestra los trenes disponibles en el momento de abrirlo.

En este ejemplo construiremos un mapa que consulta periódicamente la posición de los trenes de Ferrocarrils de la Generalitat de Catalunya (FGC). También usaremos una segunda API para colorear cada tren según su línea. La actividad permite observar un flujo habitual en una aplicación de ciudad inteligente: obtener datos actualizados de un servicio, relacionarlos con información descriptiva y representarlos en un mapa.

> **Nota sobre los datos:** la posición se actualiza cuando FGC publica una nueva respuesta. La frecuencia de consulta del navegador no implica que la fuente se actualice con esa misma frecuencia.

## 1. Explorar las API de FGC

FGC publica dos conjuntos de datos que combinaremos:

- [Posicionamiento de los trenes](https://dadesobertes.fgc.cat/explore/assets/posicionament-dels-trens/?flg=es-es): posiciones y atributos de los trenes en servicio, como línea, origen, destino y próximas paradas.
- [Líneas de la red FGC](https://dadesobertes.fgc.cat/explore/assets/lineas-red-fgc/?flg=es-es): información de las líneas, incluido su código y color.

La plataforma ofrece una API de exploración. Para descargar los datos directamente usamos estos endpoints de exportación:

```text
https://dadesobertes.fgc.cat/api/explore/v2.1/catalog/datasets/posicionament-dels-trens/exports/geojson?lang=es&timezone=Europe%2FMadrid
https://dadesobertes.fgc.cat/api/explore/v2.1/catalog/datasets/lineas-red-fgc/exports/json?lang=es&timezone=Europe%2FMadrid
```

El primer endpoint devuelve un `FeatureCollection` GeoJSON; el segundo, una lista JSON. Las respuestas pueden variar: los trenes solo aparecen mientras la fuente los publica y algunos atributos pueden estar vacíos.

## 2. Crear el mapa base

Creamos una carpeta llamada `fgc-realtime` y, dentro, un archivo `index.html`. Empezamos cargando Leaflet, un mapa centrado en Cataluña y una capa base de OpenStreetMap. Fijamos la versión de Leaflet para que el ejemplo no cambie de forma inesperada.

```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<div id="map"></div>
<script>
  const map = L.map("map").setView([41.55, 1.95], 8);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);
</script>
```

El contenedor `#map` necesita una altura definida en CSS; el código completo del final incluye también el diseño del panel de estado.

## 3. Descargar las líneas y preparar sus colores

Primero descargamos el catálogo de líneas. Creamos un diccionario donde cada `route_id` apunta a su color. Esto evita recorrer la lista de líneas cada vez que se representa un tren.

```js
const LINEAS_URL = "https://dadesobertes.fgc.cat/api/explore/v2.1/catalog/datasets/lineas-red-fgc/exports/json?lang=es&timezone=Europe%2FMadrid";
const coloresLinea = new Map();

async function cargarLineas() {
  const respuesta = await fetch(LINEAS_URL);
  if (!respuesta.ok) throw new Error(`Error al cargar líneas: ${respuesta.status}`);

  const lineas = await respuesta.json();
  lineas.forEach((linea) => {
    if (linea.route_id && linea.route_color) {
      coloresLinea.set(linea.route_id.toUpperCase(), `#${linea.route_color}`);
    }
  });
}
```

El valor de `route_color` se publica sin el símbolo `#`, por eso lo añadimos al construir el color CSS. Si una línea no está en la tabla, usaremos gris como color de reserva.

## 4. Consultar el GeoJSON y dibujar los trenes

La API de posiciones devuelve puntos GeoJSON. Leaflet interpreta las coordenadas y genera un marcador circular para cada tren. Usamos el identificador del tren como clave para reconocerlo en la siguiente actualización.

```js
const TRENES_URL = "https://dadesobertes.fgc.cat/api/explore/v2.1/catalog/datasets/posicionament-dels-trens/exports/geojson?lang=es&timezone=Europe%2FMadrid";
const marcadores = new Map();

function crearMarcador(feature, latlng) {
  const linea = String(feature.properties?.lin ?? "").toUpperCase();
  const color = coloresLinea.get(linea) ?? "#666666";

  return L.circleMarker(latlng, {
    radius: 7,
    color: "#ffffff",
    weight: 2,
    fillColor: color,
    fillOpacity: 0.9
  });
}
```

Con una `Map` de JavaScript podremos mover los marcadores existentes, crear los nuevos y eliminar los que ya no llegan en la respuesta.

## 5. Actualizar posiciones y ventanas emergentes

En cada consulta recorremos las entidades recibidas. Si el tren ya tiene marcador, cambiamos su posición y su contenido; si es nuevo, lo añadimos. Al final retiramos los marcadores que no aparecieron en esta respuesta.

```js
function textoSeguro(valor) {
  return String(valor ?? "No disponible");
}

function contenidoPopup(datos) {
  const popup = document.createElement("div");
  const titulo = document.createElement("strong");
  titulo.textContent = `Tren ${textoSeguro(datos.ut || datos.id)}`;
  popup.append(titulo);

  const detalle = document.createElement("p");
  detalle.textContent = `Línea ${textoSeguro(datos.lin)} · ${textoSeguro(datos.origen)} → ${textoSeguro(datos.desti)}`;
  popup.append(detalle);
  return popup;
}

async function actualizarTrenes() {
  const respuesta = await fetch(TRENES_URL);
  if (!respuesta.ok) throw new Error(`Error al cargar trenes: ${respuesta.status}`);
  const geojson = await respuesta.json();
  const vistos = new Set();

  geojson.features.forEach((feature) => {
    if (feature.geometry?.type !== "Point") return;
    const datos = feature.properties ?? {};
    const id = String(datos.id ?? datos.ut ?? "");
    if (!id) return;
    vistos.add(id);

    const [lng, lat] = feature.geometry.coordinates;
    const posicion = L.latLng(lat, lng);
    let marcador = marcadores.get(id);
    if (!marcador) {
      marcador = crearMarcador(feature, posicion).addTo(map);
      marcador.bindPopup(contenidoPopup(datos));
      marcadores.set(id, marcador);
    } else {
      marcador.setLatLng(posicion);
      marcador.setPopupContent(contenidoPopup(datos));
    }
  });

  marcadores.forEach((marcador, id) => {
    if (!vistos.has(id)) {
      map.removeLayer(marcador);
      marcadores.delete(id);
    }
  });
  return geojson.features.length;
}
```

El contenido del popup se construye con `textContent`. Así los valores recibidos de la API se muestran como texto y no se interpretan como HTML.

## 6. Ejecutar actualizaciones periódicas

Hacemos una primera consulta al abrir la página y repetimos la petición cada 15 segundos. También mostramos el número de trenes recibido y la hora de la última consulta. Si hay un error, lo comunicamos en el panel sin detener el resto de la aplicación.

```js
async function iniciar() {
  try {
    await cargarLineas();
    await actualizarTrenes();
    window.setInterval(actualizarTrenes, INTERVALO_MS);
  } catch (error) {
    document.querySelector("#estado").textContent = `No se pudieron cargar los datos: ${error.message}`;
  }
}

iniciar();
setInterval(iniciar, 15_000);
```

## Actividad breve en clase (5–10 minutos)

🟦 **Pregunta y prueba**

1. Abre el visor y pulsa un tren para consultar la línea y el sentido del viaje.
2. En el código, cambia temporalmente el intervalo de 15 segundos a 5 segundos.
3. ¿Qué cambia en el mapa? ¿Puedes asegurar que la posición del tren se actualiza cada 5 segundos? Explica la diferencia entre la frecuencia de consulta y la frecuencia de actualización de la fuente.

## Código completo

Guarda este contenido como `index.html` dentro de `fgc-realtime`. Abre el archivo en un navegador con conexión a Internet. Si el navegador limita peticiones desde archivos locales, ejecútalo desde un servidor local sencillo (por ejemplo, la extensión Live Server de Visual Studio Code).

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Trenes FGC en tiempo real</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    html, body { height: 100%; margin: 0; font-family: system-ui, sans-serif; }
    #map { height: 100%; }
    #estado { position: absolute; z-index: 1000; top: 12px; left: 60px; max-width: min(520px, calc(100vw - 100px)); padding: 9px 12px; border-radius: 6px; background: white; box-shadow: 0 1px 5px #5558; font-size: 14px; }
    .popup-detalle { margin: 5px 0 0; }
  </style>
</head>
<body>
  <div id="estado" role="status">Conectando con los datos de FGC…</div>
  <div id="map" aria-label="Mapa de posiciones de trenes FGC"></div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const TRENES_URL = "https://dadesobertes.fgc.cat/api/explore/v2.1/catalog/datasets/posicionament-dels-trens/exports/geojson?lang=es&timezone=Europe%2FMadrid";
    const LINEAS_URL = "https://dadesobertes.fgc.cat/api/explore/v2.1/catalog/datasets/lineas-red-fgc/exports/json?lang=es&timezone=Europe%2FMadrid";
    const INTERVALO_MS = 15_000;
    const map = L.map("map").setView([41.55, 1.95], 8);
    const coloresLinea = new Map();
    const marcadores = new Map();
    let actualizacionEnCurso = false;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap contributors</a>",
      maxZoom: 19
    }).addTo(map);

    async function cargarLineas() {
      const respuesta = await fetch(LINEAS_URL);
      if (!respuesta.ok) throw new Error(`Error al cargar líneas: ${respuesta.status}`);
      const lineas = await respuesta.json();
      lineas.forEach((linea) => {
        if (linea.route_id && linea.route_color) {
          coloresLinea.set(linea.route_id.toUpperCase(), `#${linea.route_color}`);
        }
      });
    }

    function colorTren(datos) {
      return coloresLinea.get(String(datos.lin ?? "").toUpperCase()) ?? "#666666";
    }

    function contenidoPopup(datos) {
      const contenedor = document.createElement("div");
      const titulo = document.createElement("strong");
      titulo.textContent = `Tren ${String(datos.ut ?? datos.id ?? "No disponible")}`;
      const detalle = document.createElement("p");
      detalle.className = "popup-detalle";
      detalle.textContent = `Línea ${String(datos.lin ?? "No disponible")} · ${String(datos.origen ?? "No disponible")} → ${String(datos.desti ?? "No disponible")}`;
      contenedor.append(titulo, detalle);
      return contenedor;
    }

    function estiloTren(datos) {
      const color = colorTren(datos);
      return { radius: 7, color: "#ffffff", weight: 2, fillColor: color, fillOpacity: 0.9 };
    }

    async function actualizarTrenes() {
      if (actualizacionEnCurso) return;
      actualizacionEnCurso = true;
      const estado = document.querySelector("#estado");
      try {
        const respuesta = await fetch(TRENES_URL, { cache: "no-store" });
        if (!respuesta.ok) throw new Error(`Error al cargar trenes: ${respuesta.status}`);
        const geojson = await respuesta.json();
        if (!Array.isArray(geojson.features)) throw new Error("La respuesta no contiene una lista de entidades GeoJSON");
        const vistos = new Set();

        geojson.features.forEach((feature) => {
          if (feature.geometry?.type !== "Point") return;
          const datos = feature.properties ?? {};
          const id = String(datos.id ?? datos.ut ?? "");
          const coordenadas = feature.geometry.coordinates;
          if (!id || !Array.isArray(coordenadas) || coordenadas.length < 2) return;
          const [lng, lat] = coordenadas;
          if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;
          vistos.add(id);
          const posicion = L.latLng(lat, lng);
          let marcador = marcadores.get(id);

          if (!marcador) {
            marcador = L.circleMarker(posicion, estiloTren(datos)).addTo(map);
            marcador.bindPopup(contenidoPopup(datos));
            marcadores.set(id, marcador);
          } else {
            marcador.setLatLng(posicion);
            marcador.setStyle(estiloTren(datos));
            marcador.setPopupContent(contenidoPopup(datos));
          }
        });

        marcadores.forEach((marcador, id) => {
          if (!vistos.has(id)) {
            map.removeLayer(marcador);
            marcadores.delete(id);
          }
        });

        const hora = new Date().toLocaleTimeString("es-ES");
        estado.textContent = `${vistos.size} trenes recibidos · última consulta: ${hora}`;
      } catch (error) {
        estado.textContent = `No se pudieron actualizar los trenes: ${error.message}`;
      } finally {
        actualizacionEnCurso = false;
      }
    }

    async function iniciar() {
      const estado = document.querySelector("#estado");
      try {
        await cargarLineas();
        await actualizarTrenes();
        window.setInterval(actualizarTrenes, INTERVALO_MS);
      } catch (error) {
        estado.textContent = `No se pudieron iniciar los datos de FGC: ${error.message}`;
      }
    }

    iniciar();
  </script>
</body>
</html>
```

## Referencias

- [Datos abiertos de FGC: posicionamiento de trenes](https://dadesobertes.fgc.cat/explore/assets/posicionament-dels-trens/?flg=es-es).
- [Datos abiertos de FGC: líneas de la red](https://dadesobertes.fgc.cat/explore/assets/lineas-red-fgc/?flg=es-es).
- [Documentación de la API de exploración de FGC](https://dadesobertes.fgc.cat/api-console/explore/v2.1/).
- [Leaflet: guía de inicio rápido](https://leafletjs.com/examples/quick-start/).

**Siguiente:** [GTFS con EMT València](18_ejemplo_gtfs.md).
