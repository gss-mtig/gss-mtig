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
    const positionStatus = participant.position ? "en el mapa" : "elige una posición";
    item.textContent = `${participant.avatar} ${participant.name} — ${positionStatus}`;
    rosterElement.append(item);
  }
}

function joinExpedition() {
  if (!profile || !socket.connected) return;
  currentUserId = socket.id;
  socket.emit("participant:join", profile, (result) => {
    if (!result?.ok) {
      statusElement.textContent = "No se pudo entrar en la expedición. Inténtalo de nuevo.";
      return;
    }
    statusElement.textContent = "Ya estás dentro. Haz clic en el mapa para mover tu avatar.";
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
    statusElement.textContent = "Entra con un alias antes de elegir tu posición.";
    return;
  }
  socket.emit("participant:move", {
    lat: event.latlng.lat,
    lng: event.latlng.lng,
  });
});

socket.on("connect", () => {
  statusElement.textContent = "Conectado al servidor. Elige un alias para entrar.";
  joinButton.disabled = false;
  joinButton.textContent = profile ? "Volver a la expedición" : "Entrar en la expedición";
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
