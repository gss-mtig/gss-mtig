# Mapa colaborativo: expedición urbana en tiempo real

En este ejemplo cada persona entra en una expedición con un alias y un avatar. Al hacer clic en el mapa, mueve su marcador y el resto de participantes ve la nueva posición al instante. Usaremos posiciones simuladas; la página no solicita acceso al GPS.

**Resultado final:** [abre la vista previa de la expedición](https://mapa-expedicion-realtime.bolosig.workers.dev/cloudflare).

La aplicación usa Leaflet para el mapa y [Socket.IO](https://socket.io/) para intercambiar eventos entre el navegador y el servidor. El servidor guarda el alias, el avatar y la última posición de cada conexión. Cuando llega un cambio, lo retransmite a los demás clientes.

## Qué veremos en el mapa

- Cada persona elige un alias y uno de los avatares disponibles.
- La lista indica quién está conectado y quién ya ha elegido una posición.
- Un clic mueve el marcador existente de esa persona; no añade un punto nuevo.
- Quienes se conectan más tarde reciben la lista y las posiciones que ya están guardadas.
- Al cerrar una pestaña, el servidor elimina a esa persona y actualiza la lista.

Las posiciones solo viven en la memoria del servidor y desaparecen cuando se detiene. Para la demostración local se pueden abrir varias pestañas; para que participe toda la clase, los equipos deben abrir la dirección de un mismo servidor accesible en la red local.

## Construir la aplicación paso a paso

Crea una carpeta `mapa-expedicion-realtime` con un archivo `server.js` y una carpeta `public` que contenga `index.html` y `app.js`. El proyecto descargable ya incluye esos archivos y su `package.json`.

### 1. Crear el mapa y el formulario de entrada

El HTML tiene un panel para elegir alias y avatar, una lista de participantes y un contenedor para el mapa. Leaflet dibuja el mapa centrado en Barcelona:

```html
<form id="join-form">
  <label for="name">Tu alias</label>
  <input id="name" maxlength="24" required />
  <label for="avatar">Tu avatar</label>
  <select id="avatar">
    <option value="🦊">Zorro</option>
    <option value="🐼">Panda</option>
    <option value="🐢">Tortuga</option>
  </select>
  <button type="submit">Entrar en la expedición</button>
</form>
<div id="map"></div>
```

```js
const map = L.map("map").setView([41.387, 2.17], 13);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);
```

### 2. Conectar el navegador con Socket.IO

El servidor sirve el cliente de Socket.IO en `/socket.io/socket.io.js`. Al cargar la página, `io()` se conecta al mismo servidor que entregó el HTML:

```html
<script src="/socket.io/socket.io.js"></script>
<script src="app.js"></script>
```

```js
const socket = io();
```

El cliente y el servidor intercambian eventos con nombres acordados. En este ejemplo usaremos `participant:join`, `participant:move` y `participants:snapshot`.

### 3. Registrar participantes y enviar el estado inicial

El servidor mantiene un `Map` en memoria, usando el identificador de conexión como clave. Cuando un cliente se conecta, recibe una copia del estado actual; cuando entra con un alias, el servidor agrega su perfil y difunde la nueva lista:

```js
const participants = new Map();

io.on("connection", (socket) => {
  socket.emit("participants:snapshot", Array.from(participants.values()));

  socket.on("participant:join", (profile, acknowledge) => {
    const participant = {
      id: socket.id,
      name: profile.name,
      avatar: profile.avatar,
      position: null,
    };
    participants.set(socket.id, participant);
    acknowledge({ ok: true, id: socket.id });
    io.emit("participants:snapshot", Array.from(participants.values()));
  });
});
```

El navegador envía el alias y el avatar elegidos al enviar el formulario. El servidor limita el alias y acepta solo los avatares previstos para evitar introducir contenido HTML arbitrario.

### 4. Enviar la posición cuando alguien pulsa el mapa

Leaflet entrega el punto pulsado como latitud y longitud. El cliente lo envía como el evento `participant:move`:

```js
map.on("click", (event) => {
  socket.emit("participant:move", {
    lat: event.latlng.lat,
    lng: event.latlng.lng,
  });
});
```

El servidor comprueba que existe un participante conectado y que las coordenadas están dentro de los límites geográficos antes de actualizar su posición y emitir `participant:moved` a todos.

### 5. Mover el avatar y mostrar quién está conectado

En el navegador, otro `Map` relaciona cada identificador de participante con su marcador Leaflet. Si ya existe, se cambia su posición; si es la primera vez, se crea el marcador:

```js
let marker = markers.get(participant.id);
const coordinates = [participant.position.lat, participant.position.lng];

if (marker) {
  marker.setLatLng(coordinates);
} else {
  marker = L.marker(coordinates, { icon }).addTo(map);
  markers.set(participant.id, marker);
}
```

Cada `participants:snapshot` actualiza el contador y la lista. Si alguien se desconecta, el servidor lo quita de su `Map` y vuelve a difundir la lista; los navegadores eliminan su marcador.

### 6. Instalar y ejecutar el servidor

Necesitas [Node.js](https://nodejs.org/es/) 18 o posterior. Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
npm install
npm start
```

Abre `http://localhost:3000`, entra con un alias y pulsa el mapa. Abre una segunda pestaña en la misma dirección y entra con otro alias: verás cómo ambos avatares aparecen y se mueven en las dos pestañas.

Para una demostración en varios equipos, inicia el servidor en un ordenador accesible para la clase y abre desde los demás la dirección de ese ordenador, por ejemplo `http://192.168.1.20:3000`. Todos deben estar conectados al mismo servidor.

## Código completo

El código completo coincide con los archivos del [ejemplo descargable](ejemplos/mapa-expedicion-realtime/README.md). Conserva la validación de coordenadas, la lista de participantes, las reconexiones y el diseño adaptable.

### Código de `server.js`

```js
const express = require("express");
const http = require("node:http");
const path = require("node:path");
const { Server } = require("socket.io");

const app = express();
const httpServer = http.createServer(app);
const io = new Server(httpServer);
const participants = new Map();
const allowedAvatars = new Set(["🦊", "🐼", "🐢", "🐙", "🐝", "🦉"]);

app.use(express.static(path.join(__dirname, "public")));

function participantList() {
  return Array.from(participants.values());
}

function validPosition(position) {
  if (!position || typeof position !== "object") return null;
  const lat = Number(position.lat);
  const lng = Number(position.lng);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  if (lat < -90 || lat > 90 || lng < -180 || lng > 180) return null;
  return { lat, lng };
}

io.on("connection", (socket) => {
  socket.emit("participants:snapshot", participantList());

  socket.on("participant:join", (payload, acknowledge) => {
    const name =
      String(payload?.name || "")
        .trim()
        .slice(0, 24) || "Explorador";
    const avatar = allowedAvatars.has(payload?.avatar) ? payload.avatar : "🦊";
    const participant = { id: socket.id, name, avatar, position: null };
    participants.set(socket.id, participant);

    if (typeof acknowledge === "function") {
      acknowledge({ ok: true, id: socket.id });
    }
    io.emit("participants:snapshot", participantList());
  });

  socket.on("participant:move", (position) => {
    const participant = participants.get(socket.id);
    const safePosition = validPosition(position);
    if (!participant || !safePosition) return;

    participant.position = safePosition;
    io.emit("participant:moved", participant);
  });

  socket.on("disconnect", () => {
    if (participants.delete(socket.id)) {
      io.emit("participants:snapshot", participantList());
    }
  });
});

const port = Number(process.env.PORT || 3000);
const host = process.env.HOST || "0.0.0.0";
httpServer.listen(port, host, () => {
  console.log(`Mapa de la expedición disponible en http://localhost:${port}`);
  console.log(
    `Para otros equipos de la red local, usa la IP de este ordenador y el puerto ${port}.`,
  );
});
```

### Código de `public/index.html`

```html
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>La expedición urbana de la clase</title>
    <link
      rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
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
        color: #172033;
      }
      #app {
        display: grid;
        grid-template-columns: minmax(280px, 350px) minmax(0, 1fr);
        height: 100vh;
      }
      aside {
        overflow: auto;
        padding: 1.1rem;
        background: #f5f8fc;
        border-right: 1px solid #d6dfeb;
      }
      h1 {
        margin: 0 0 0.45rem;
        font-size: 1.4rem;
      }
      p {
        margin: 0.5rem 0;
      }
      label {
        display: block;
        margin-top: 0.8rem;
        font-weight: 650;
      }
      input,
      select,
      button {
        width: 100%;
        min-height: 2.5rem;
        margin-top: 0.3rem;
        padding: 0.5rem 0.6rem;
        font: inherit;
      }
      button {
        border: 0;
        border-radius: 0.4rem;
        color: white;
        background: #1457a6;
        cursor: pointer;
      }
      button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      #status {
        min-height: 2.6rem;
        margin-top: 0.8rem;
        padding: 0.55rem;
        border-radius: 0.35rem;
        background: white;
      }
      #roster {
        padding-left: 1.4rem;
      }
      #roster li {
        margin: 0.35rem 0;
      }
      #map {
        min-width: 0;
        height: 100vh;
      }
      .avatar-marker {
        display: grid;
        place-items: center;
        width: 38px;
        height: 38px;
        border: 2px solid white;
        border-radius: 50%;
        background: #1457a6;
        box-shadow: 0 1px 7px #17203366;
        font-size: 23px;
      }
      .note {
        color: #475569;
        font-size: 0.9rem;
      }
      @media (max-width: 700px) {
        #app {
          grid-template-columns: minmax(0, 1fr);
          grid-template-rows: minmax(320px, 52vh) auto;
          height: auto;
          min-height: 100vh;
        }
        #map {
          grid-column: 1;
          grid-row: 1;
          height: 52vh;
          min-height: 320px;
        }
        aside {
          grid-column: 1;
          grid-row: 2;
          border-right: 0;
          border-top: 1px solid #d6dfeb;
        }
      }
    </style>
  </head>
  <body>
    <main id="app">
      <aside>
        <h1>🧭 Expedición urbana</h1>
        <p>
          Elige un alias y un avatar. Haz clic en el mapa para mover tu
          posición; el resto de la clase verá el cambio al instante.
        </p>

        <form id="join-form">
          <label for="name">Tu alias</label>
          <input
            id="name"
            maxlength="24"
            placeholder="Por ejemplo, Alex"
            required
          />
          <label for="avatar">Tu avatar</label>
          <select id="avatar">
            <option value="🦊">🦊 Zorro</option>
            <option value="🐼">🐼 Panda</option>
            <option value="🐢">🐢 Tortuga</option>
            <option value="🐙">🐙 Pulpo</option>
            <option value="🐝">🐝 Abeja</option>
            <option value="🦉">🦉 Búho</option>
          </select>
          <button id="join-button" type="submit" disabled>Conectando…</button>
        </form>

        <p id="status" role="status" aria-live="polite">
          Conectando con el servidor…
        </p>
        <h2>En la expedición: <span id="count">0</span></h2>
        <ol id="roster"></ol>
        <p class="note">
          La posición se simula con clics; la página no solicita tu ubicación
          GPS. Abre otra pestaña u otro equipo para simular más participantes.
        </p>
      </aside>
      <div id="map" aria-label="Mapa colaborativo de la clase"></div>
    </main>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="/socket.io/socket.io.js"></script>
    <script src="app.js"></script>
  </body>
</html>
```

### Código de `public/app.js`

```js
const map = L.map("map").setView([41.387, 2.17], 13);
const socket = io();
const markers = new Map();
const participants = new Map();
const joinForm = document.getElementById("join-form");
const nameInput = document.getElementById("name");
const avatarInput = document.getElementById("avatar");
const joinButton = document.getElementById("join-button");
const statusElement = document.getElementById("status");
const countElement = document.getElementById("count");
const rosterElement = document.getElementById("roster");
let currentUserId = null;
let profile = null;

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
  maxZoom: 19,
}).addTo(map);

function showParticipant(participant) {
  if (!participant.position) return;
  const coordinates = [participant.position.lat, participant.position.lng];
  let marker = markers.get(participant.id);

  if (!marker) {
    const icon = L.divIcon({
      className: "",
      html: `<span class="avatar-marker">${participant.avatar}</span>`,
      iconSize: [38, 38],
      iconAnchor: [19, 19],
    });
    marker = L.marker(coordinates, { icon }).addTo(map);
    const popup = document.createElement("span");
    popup.textContent = `${participant.avatar} ${participant.name}`;
    marker.bindPopup(popup);
    markers.set(participant.id, marker);
  } else {
    marker.setLatLng(coordinates);
  }
}

function renderParticipants(list) {
  const activeIds = new Set(list.map((participant) => participant.id));
  for (const [id, marker] of markers) {
    if (!activeIds.has(id)) {
      map.removeLayer(marker);
      markers.delete(id);
    }
  }

  participants.clear();
  list.forEach((participant) => {
    participants.set(participant.id, participant);
    showParticipant(participant);
  });

  countElement.textContent = String(participants.size);
  rosterElement.replaceChildren();
  for (const participant of participants.values()) {
    const item = document.createElement("li");
    const positionStatus = participant.position
      ? "en el mapa"
      : "elige una posición";
    item.textContent = `${participant.avatar} ${participant.name} — ${positionStatus}`;
    rosterElement.append(item);
  }
}

function joinExpedition() {
  if (!profile || !socket.connected) return;
  currentUserId = socket.id;
  socket.emit("participant:join", profile, (result) => {
    if (!result?.ok) {
      statusElement.textContent =
        "No se pudo entrar en la expedición. Inténtalo de nuevo.";
      return;
    }
    statusElement.textContent =
      "Ya estás dentro. Haz clic en el mapa para mover tu avatar.";
    joinButton.disabled = true;
    joinButton.textContent = "Ya estás en la expedición";
  });
}

joinForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const name = nameInput.value.trim();
  if (!name) {
    statusElement.textContent = "Escribe un alias antes de entrar.";
    nameInput.focus();
    return;
  }
  profile = { name: name.slice(0, 24), avatar: avatarInput.value };
  joinButton.disabled = true;
  joinButton.textContent = "Entrando…";
  joinExpedition();
});

map.on("click", (event) => {
  if (!currentUserId || !socket.connected) {
    statusElement.textContent =
      "Entra con un alias antes de elegir tu posición.";
    return;
  }
  socket.emit("participant:move", {
    lat: event.latlng.lat,
    lng: event.latlng.lng,
  });
});

socket.on("connect", () => {
  statusElement.textContent =
    "Conectado al servidor. Elige un alias para entrar.";
  joinButton.disabled = false;
  joinButton.textContent = profile
    ? "Volver a la expedición"
    : "Entrar en la expedición";
  if (profile) joinExpedition();
});

socket.on("disconnect", () => {
  currentUserId = null;
  if (profile) {
    joinButton.disabled = false;
    joinButton.textContent = "Reconectando…";
  }
  statusElement.textContent = "Se perdió la conexión. Esperando al servidor…";
});

socket.on("participants:snapshot", renderParticipants);

socket.on("participant:moved", (participant) => {
  participants.set(participant.id, participant);
  showParticipant(participant);
  renderParticipants(Array.from(participants.values()));
});
```

## Prueba breve en clase

!!! question "5–10 minutos · sin entregar"
Abre dos pestañas, entra con dos alias distintos y mueve ambos avatares hasta un punto de encuentro. Cierra una pestaña y observa cómo cambian la lista de participantes y el contador en la otra.

## Ejercicio opcional para casa

Añade un botón **Centrar en la expedición** que ajuste el mapa para mostrar a todos los participantes que ya eligieron posición. Comprueba el comportamiento con al menos dos navegadores conectados.

## Referencias

- [Socket.IO: introducción y documentación oficial (inglés)](https://socket.io/docs/v4/)
- [Socket.IO: inicializar el cliente (inglés)](https://socket.io/docs/v4/client-initialization/)
- [Node.js: sitio oficial en español](https://nodejs.org/es/)
- [Leaflet: referencia de la API (inglés)](https://leafletjs.com/reference.html)
- [OpenStreetMap: atribución](https://www.openstreetmap.org/copyright)
