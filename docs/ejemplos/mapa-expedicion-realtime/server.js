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
    const name = String(payload?.name || "").trim().slice(0, 24) || "Explorador";
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
  console.log(`Para otros equipos de la red local, usa la IP de este ordenador y el puerto ${port}.`);
});
