const map = L.map("map").setView([41.387, 2.17], 13);
const markers = new Map();
const participants = new Map();
const joinForm = document.getElementById("join-form");
const nameInput = document.getElementById("name");
const avatarInput = document.getElementById("avatar");
const joinButton = document.getElementById("join-button");
const statusElement = document.getElementById("status");
const countElement = document.getElementById("count");
const rosterElement = document.getElementById("roster");
let socket;
let currentUserId = null;
let profile = null;
let reconnectDelay = 1000;

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
  maxZoom: 19,
}).addTo(map);

function send(event, data) {
  if (socket?.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ event, data }));
  }
}

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
    const positionStatus = participant.position ? "en el mapa" : "elige una posición";
    item.textContent = `${participant.avatar} ${participant.name} — ${positionStatus}`;
    rosterElement.append(item);
  }
}

function connect() {
  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  socket = new WebSocket(`${protocol}//${location.host}/api/ws`);

  socket.addEventListener("open", () => {
    reconnectDelay = 1000;
    statusElement.textContent = "Conectado al servidor. Elige un alias para entrar.";
    joinButton.disabled = false;
    joinButton.textContent = profile ? "Volver a la expedición" : "Entrar en la expedición";
    if (profile) send("participant:join", profile);
  });

  socket.addEventListener("message", (message) => {
    let packet;
    try {
      packet = JSON.parse(message.data);
    } catch {
      return;
    }

    if (packet.event === "participants:snapshot") renderParticipants(packet.data);
    if (packet.event === "participant:joined" && packet.data?.ok) {
      currentUserId = packet.data.id;
      statusElement.textContent = "Ya estás dentro. Haz clic en el mapa para mover tu avatar.";
      joinButton.disabled = true;
      joinButton.textContent = "Ya estás en la expedición";
    }
  });

  socket.addEventListener("close", () => {
    currentUserId = null;
    joinButton.disabled = true;
    if (profile) joinButton.textContent = "Reconectando…";
    statusElement.textContent = "Se perdió la conexión. Esperando al servidor…";
    window.setTimeout(connect, reconnectDelay);
    reconnectDelay = Math.min(reconnectDelay * 2, 10000);
  });

  socket.addEventListener("error", () => socket.close());
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
  send("participant:join", profile);
});

map.on("click", (event) => {
  if (!currentUserId || socket?.readyState !== WebSocket.OPEN) {
    statusElement.textContent = "Entra con un alias antes de elegir tu posición.";
    return;
  }
  send("participant:move", { lat: event.latlng.lat, lng: event.latlng.lng });
});

connect();
