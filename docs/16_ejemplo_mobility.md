# Isócronas para analizar la accesibilidad urbana

Una **isócrona** representa las zonas que se pueden alcanzar desde un punto en un tiempo determinado y con un modo de desplazamiento concreto. En esta actividad consultamos [OpenRouteService](https://openrouteservice.org/), un servicio basado en datos de OpenStreetMap. Comparamos dos formas de consumirlo desde una aplicación Leaflet: el control del plugin `leaflet.reachability` y una petición propia con `fetch`.

**Resultado final:** [abre el visor de isócronas](ejemplos/mobility-isochrones/index.html). El código completo que aparece más abajo es el mismo archivo `index.html` del visor.

## Qué hace el ejemplo

El mapa empieza centrado en Barcelona. La persona que lo prueba introduce su propia clave de OpenRouteService. Puede activar el control de `leaflet.reachability`, que permite elegir sus parámetros y dibujar desde el mapa, o usar el formulario de la página, que envía una petición `POST` propia con `fetch`. Ambas opciones dibujan isócronas sobre Leaflet.

La petición incluye coordenadas en orden **longitud, latitud**, el perfil de transporte y el intervalo en segundos. La respuesta depende de la red de calles y del perfil elegido: no es un círculo alrededor del origen.

El tutorial anterior usaba `api.openrouteservice.org`. OpenRouteService está trasladando sus servicios a `api.heigit.org/openrouteservice`; esta versión usa el endpoint actual y las claves personales sirven para autenticar la petición.

## Construir el visor paso a paso

Los siguientes fragmentos muestran las partes principales de la aplicación. Añádelos al archivo `index.html` siguiendo el orden; al final encontrarás el archivo completo con el diseño, las comprobaciones de errores y las dos formas de consultar el servicio.

### 1. Preparar el mapa y una capa GeoJSON

El mapa necesita un elemento HTML con el identificador `map`. Leaflet lo convierte en un mapa interactivo y `L.geoJSON` será la capa donde mostraremos las isócronas que devuelva el servicio.

```html
<div id="map"></div>
```

```js
const map = L.map('map').setView([41.3874, 2.1686], 13);
const isochrones = L.geoJSON([]).addTo(map);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);
```

La coordenada inicial se escribe como `[latitud, longitud]`, que es el orden que espera Leaflet para centrar el mapa.

### 2. Añadir el control de `leaflet.reachability`

Incluye el CSS y el JavaScript del plugin en el `<head>` y después de Leaflet, respectivamente. La versión `v2.0.2` ya usa el endpoint actual de OpenRouteService. Al pulsar el botón de activación, el control recibe la clave introducida por el usuario:

```js
let reachabilityControl;

activateControlButton.addEventListener('click', () => {
  const apiKey = keyInput.value.trim();
  if (!apiKey) return;

  reachabilityControl = L.control.reachability({
    apiKey,
    position: 'topright',
    collapsed: false
  }).addTo(map);
});
```

El plugin gestiona la selección del perfil, el tiempo y la petición. El usuario activa su modo de dibujo en el control y elige el punto de origen sobre el mapa.

### 3. Construir una petición propia con `fetch`

Para comparar con el plugin, el mapa también permite consultar el servicio directamente. Leaflet entrega el clic como latitud y longitud, pero la API espera las coordenadas como **longitud, latitud**. El intervalo de tiempo se envía en segundos:

```js
const coordinates = [event.latlng.lng, event.latlng.lat];
const rangeSeconds = Number(minutesInput.value) * 60;

const response = await fetch(`${API_BASE}/${profileInput.value}`, {
  method: 'POST',
  headers: {
    'Authorization': keyInput.value.trim(),
    'Content-Type': 'application/json',
    'Accept': 'application/geo+json'
  },
  body: JSON.stringify({
    locations: [coordinates],
    range_type: 'time',
    range: [rangeSeconds],
    location_type: 'start'
  })
});
```

`profileInput.value` elige entre caminar, ir en bicicleta o conducir. La respuesta es GeoJSON, así que podemos añadirla a la capa de Leaflet después de comprobar que la petición ha terminado correctamente.

### 4. Comprobar y dibujar la respuesta

Una petición puede fallar por una clave incorrecta, un límite de uso o un problema de red. Comprobamos el estado HTTP y que haya entidades GeoJSON antes de actualizar el mapa:

```js
const result = await response.json();
if (!response.ok) {
  throw new Error(result.error?.message || `Error HTTP ${response.status}`);
}
if (result.type !== 'FeatureCollection' || !result.features?.length) {
  throw new Error('La respuesta no contiene isócronas GeoJSON.');
}

isochrones.clearLayers();
isochrones.addData(result);
```

`clearLayers()` borra el resultado anterior antes de mostrar el nuevo. El código completo también añade un marcador en el punto elegido y comunica el resultado o el error en el panel.

### Probar el visor

1. Abre [OpenRouteService](https://openrouteservice.org/) y crea una clave personal si todavía no tienes una.
2. Abre el [visor de isócronas](ejemplos/mobility-isochrones/index.html) y pega la clave en el campo correspondiente.
3. Pulsa **Activar control de Leaflet**. En el control que aparece arriba a la derecha, elige un perfil y un tiempo, activa el modo de dibujo y pulsa un punto del mapa.
4. Elige otro origen y calcula otra isócrona con el formulario del panel. Compara ambos resultados y observa la diferencia entre usar un plugin y escribir la petición con `fetch`.

La clave se introduce en el navegador y se envía a OpenRouteService como cabecera de autorización. Por eso cualquier persona con acceso al navegador puede inspeccionar la petición. Este patrón sirve para una demostración local y para aprender a consumir una API; una aplicación pública debería proteger la clave mediante un servidor propio.

## Código completo

Guarda el siguiente código como `index.html` y ábrelo desde un servidor local (por ejemplo, `python3 -m http.server`). Así se evita depender de cómo el navegador trata los archivos abiertos directamente desde el disco.

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Isócronas con OpenRouteService</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/trafforddatalab/leaflet.reachability@v2.0.2/leaflet.reachability.css">
  <style>
    * { box-sizing: border-box; }
    html, body { height: 100%; margin: 0; font: 16px/1.45 system-ui, sans-serif; color: #172033; }
    #app {
      display: grid;
      grid-template-columns: minmax(320px, 380px) minmax(0, 1fr);
      grid-template-rows: minmax(0, 1fr);
      width: 100%;
      height: 100vh;
    }
    aside { grid-column: 1; grid-row: 1; min-width: 0; overflow: auto; padding: 1.25rem; background: #f4f7fb; }
    h1 { margin: 0 0 .5rem; font-size: 1.35rem; }
    p { margin: .6rem 0; }
    label { display: block; margin-top: 1rem; font-weight: 650; }
    input, select, button { width: 100%; min-height: 2.6rem; margin-top: .35rem; padding: .45rem .6rem; font: inherit; }
    button { border: 0; border-radius: .35rem; color: white; background: #1457a6; cursor: pointer; }
    button:disabled { opacity: .6; cursor: wait; }
    #status { min-height: 3.2rem; padding: .65rem; border-radius: .35rem; background: white; }
    #map { grid-column: 2; grid-row: 1; min-width: 0; min-height: 0; height: 100vh; }
    .note { font-size: .9rem; color: #475569; }
    @media (max-width: 700px) {
      #app { grid-template-columns: minmax(0, 1fr); grid-template-rows: minmax(320px, 55vh) auto; height: auto; min-height: 100vh; }
      aside { grid-column: 1; grid-row: 2; max-height: none; border-top: 1px solid #d1d5db; }
      #map { grid-column: 1; grid-row: 1; height: 55vh; min-height: 320px; max-height: 520px; }
    }
  </style>
</head>
<body>
  <main id="app">
    <aside>
      <h1>¿Hasta dónde llego?</h1>
      <p>Introduce tu clave y prueba dos formas de solicitar isócronas: el control Leaflet o una petición propia con <code>fetch</code>.</p>

      <label for="api-key">Clave de OpenRouteService</label>
      <input id="api-key" type="password" autocomplete="off" placeholder="Pega aquí tu clave personal">
      <button id="activate-control" type="button">Activar control de Leaflet</button>
      <p class="note">También puedes usar el control de alcance que aparece arriba a la derecha del mapa.</p>

      <label for="profile">Modo de desplazamiento</label>
      <select id="profile">
        <option value="foot-walking">A pie</option>
        <option value="cycling-regular">En bicicleta</option>
        <option value="driving-car">En coche</option>
      </select>

      <label for="minutes">Tiempo máximo: <span id="minutes-label">15</span> minutos</label>
      <input id="minutes" type="range" min="5" max="30" step="5" value="15">
      <button id="clear" type="button">Borrar isócrona de fetch</button>
      <p id="status" role="status" aria-live="polite">Haz clic en el mapa para elegir el punto de partida.</p>
      <p class="note">La clave se usa desde este navegador para llamar a la API. No la compartas ni la guardes en una página pública.</p>
    </aside>
    <div id="map" aria-label="Mapa interactivo"></div>
  </main>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/trafforddatalab/leaflet.reachability@v2.0.2/leaflet.reachability.js"></script>
  <script>
    const API_BASE = 'https://api.heigit.org/openrouteservice/v2/isochrones';
    const map = L.map('map').setView([41.3874, 2.1686], 13);
    const isochrones = L.geoJSON([], {
      style: feature => ({
        color: '#1457a6',
        weight: 2,
        fillColor: '#3388ff',
        fillOpacity: Math.max(0.18, 0.5 - feature.properties.value / 9000)
      })
    }).addTo(map);
    let originMarker;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const keyInput = document.querySelector('#api-key');
    const profileInput = document.querySelector('#profile');
    const minutesInput = document.querySelector('#minutes');
    const minutesLabel = document.querySelector('#minutes-label');
    const status = document.querySelector('#status');
    const clearButton = document.querySelector('#clear');
    const activateControlButton = document.querySelector('#activate-control');
    let reachabilityControl;

    minutesInput.addEventListener('input', () => {
      minutesLabel.textContent = minutesInput.value;
    });

    clearButton.addEventListener('click', () => {
      isochrones.clearLayers();
      if (originMarker) map.removeLayer(originMarker);
      originMarker = undefined;
      status.textContent = 'Isócrona de fetch borrada. El control de Leaflet tiene su propio botón para borrar resultados.';
    });

    activateControlButton.addEventListener('click', () => {
      const apiKey = keyInput.value.trim();
      if (!apiKey) {
        status.textContent = 'Introduce tu clave antes de activar el control de Leaflet.';
        keyInput.focus();
        return;
      }

      if (reachabilityControl) map.removeControl(reachabilityControl);
      reachabilityControl = L.control.reachability({
        apiKey,
        position: 'topright',
        collapsed: false
      }).addTo(map);
      status.textContent = 'Control de Leaflet activado. Pulsa su botón de dibujar y luego el mapa.';
    });

    map.on('click', async event => {
      const apiKey = keyInput.value.trim();
      if (!apiKey) {
        status.textContent = 'Introduce tu clave de OpenRouteService antes de elegir un punto.';
        keyInput.focus();
        return;
      }

      const coordinates = [event.latlng.lng, event.latlng.lat];
      const rangeSeconds = Number(minutesInput.value) * 60;
      status.textContent = 'Consultando OpenRouteService…';
      clearButton.disabled = true;

      try {
        const response = await fetch(`${API_BASE}/${profileInput.value}`, {
          method: 'POST',
          headers: {
            'Authorization': apiKey,
            'Content-Type': 'application/json',
            'Accept': 'application/geo+json'
          },
          body: JSON.stringify({
            locations: [coordinates],
            range_type: 'time',
            range: [rangeSeconds],
            location_type: 'start'
          })
        });

        const result = await response.json();
        if (!response.ok) {
          throw new Error(result.error?.message || `La API respondió con HTTP ${response.status}.`);
        }
        if (result.type !== 'FeatureCollection' || !result.features?.length) {
          throw new Error('La respuesta no contiene isócronas en formato GeoJSON.');
        }

        isochrones.clearLayers();
        isochrones.addData(result);
        if (originMarker) map.removeLayer(originMarker);
        originMarker = L.marker(event.latlng).addTo(map).bindPopup('Punto de partida');
        status.textContent = `Isócrona calculada: ${minutesInput.value} minutos, ${profileInput.options[profileInput.selectedIndex].text.toLowerCase()}.`;
      } catch (error) {
        status.textContent = `No se pudo calcular la isócrona: ${error.message}`;
      } finally {
        clearButton.disabled = false;
      }
    });
  </script>
</body>
</html>
```

## Actividad breve en clase

!!! question "5–10 minutos · sin entregar"
    Elige un mismo origen y calcula una isócrona de 15 minutos a pie y en bicicleta. ¿Cuál cubre más superficie? Propón una razón relacionada con la red viaria o el perfil de desplazamiento. Después, cambia el origen a un punto en el borde de Barcelona y observa qué cambia.

!!! exercise "Ejercicio entregable · 2 puntos"
    Modifica la aplicación y entrega el archivo `index.html`:

    1. Añade al selector un perfil válido de OpenRouteService que no aparezca en el ejemplo y comprueba que la petición directa lo utiliza (1 punto).
    2. Modifica el intervalo de tiempo que permite elegir el control y comprueba que el parámetro `range` de la petición corresponde al nuevo valor (1 punto).

## Ejercicio opcional para casa

Modifica el ejemplo para permitir comparar dos perfiles desde el mismo origen, mostrando ambos polígonos con colores y transparencias distintas. Añade una leyenda que permita identificar cada perfil.

## Referencias

- [OpenRouteService: API de isócronas](https://openrouteservice.org/dev/#/api-docs/v2/isochrones/{profile}/post)
- [Dominio actual de la API de OpenRouteService](https://api.heigit.org/openrouteservice/)
- [Leaflet: documentación](https://leafletjs.com/reference.html)
- [OpenStreetMap: atribución](https://www.openstreetmap.org/copyright)
