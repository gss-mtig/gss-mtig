import { DurableObject } from "cloudflare:workers";

const allowedAvatars = new Set(["🦊", "🐼", "🐢", "🐙", "🐝", "🦉"]);

function participants(room) {
  return room.ctx.getWebSockets()
    .filter((socket) => socket.readyState === WebSocket.OPEN)
    .map((socket) => socket.deserializeAttachment())
    .filter((participant) => participant?.name);
}

function validPosition(position) {
  if (!position || typeof position !== "object") return null;
  const lat = Number(position.lat);
  const lng = Number(position.lng);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  if (lat < -90 || lat > 90 || lng < -180 || lng > 180) return null;
  return { lat, lng };
}

export class ExpeditionRoom extends DurableObject {
  // Este objeto coordina una sala y conserva las conexiones WebSocket al hibernar;
  // no usa SQLite ni almacena participantes en una base de datos.
  async fetch(request) {
    if (request.headers.get("Upgrade") !== "websocket") {
      return new Response("Se requiere una conexión WebSocket", { status: 426 });
    }

    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    server.serializeAttachment({ id: crypto.randomUUID(), name: "", avatar: "🦊", position: null });
    this.ctx.acceptWebSocket(server);
    server.send(JSON.stringify({ event: "participants:snapshot", data: participants(this) }));

    return new Response(null, { status: 101, webSocket: client });
  }

  webSocketMessage(socket, message) {
    if (typeof message !== "string" || message.length > 2048) return;

    let packet;
    try {
      packet = JSON.parse(message);
    } catch {
      return;
    }

    const participant = socket.deserializeAttachment();
    if (packet.event === "participant:join") {
      participant.name = String(packet.data?.name || "").trim().slice(0, 24) || "Explorador";
      participant.avatar = allowedAvatars.has(packet.data?.avatar) ? packet.data.avatar : "🦊";
      socket.serializeAttachment(participant);
      socket.send(JSON.stringify({ event: "participant:joined", data: { ok: true, id: participant.id } }));
      this.broadcastSnapshot();
      return;
    }

    if (packet.event === "participant:move" && participant.name) {
      const position = validPosition(packet.data);
      if (!position) return;
      participant.position = position;
      socket.serializeAttachment(participant);
      this.broadcastSnapshot();
    }
  }

  webSocketClose() {
    this.broadcastSnapshot();
  }

  broadcastSnapshot() {
    const packet = JSON.stringify({ event: "participants:snapshot", data: participants(this) });
    for (const socket of this.ctx.getWebSockets()) {
      if (socket.readyState === WebSocket.OPEN) socket.send(packet);
    }
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/ws") {
      const room = env.EXPEDITION_ROOM.getByName("expedicion-clase");
      return room.fetch(request);
    }

    if (url.pathname === "/") url.pathname = "/cloudflare.html";
    return env.ASSETS.fetch(new Request(url, request));
  },
};
