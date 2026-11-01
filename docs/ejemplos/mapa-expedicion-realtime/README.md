# Mapa colaborativo de la expedición

Este ejemplo incluye dos formas de ejecutar el servidor:

- **Local:** Express y Socket.IO, como en el ejercicio del curso.
- **Cloudflare:** Workers y Durable Objects con WebSockets nativos. Esta versión funciona en el plan gratuito y comparte una sala entre quienes abran el mismo enlace.

GitHub Pages solo publica archivos estáticos, así que no puede ejecutar el servidor Node.js local. En Cloudflare, el Worker y el Durable Object proporcionan la parte de servidor; Cloudflare también publica los archivos del mapa.

Aquí Durable Object significa **objeto coordinador**, no base de datos: Cloudflare enruta las conexiones de la clase a una única sala para que pueda retransmitir los cambios y mantener las conexiones al hibernar. El ejemplo no consulta SQLite ni guarda las posiciones de forma permanente. Los datos de cada participante van adjuntos a su conexión WebSocket para recuperarlos después de la hibernación; al cerrarse la conexión, se eliminan.

## Publicar en Cloudflare Free

Se necesita una cuenta Cloudflare y Node.js instalado. No hace falta Docker. Desde esta carpeta:

```bash
npm install
npm run deploy:cloudflare
```

En el primer despliegue, Wrangler pedirá iniciar sesión. Al terminar, mostrará una dirección `workers.dev`; abre el enlace raíz para compartir la versión realtime con la clase. Todos los alumnos que usen ese enlace entran en la misma expedición.

El plan gratuito tiene límites diarios de uso para Workers y Durable Objects. La sala guarda alias, avatares y posiciones solo mientras cada participante está conectado. Consulta los [límites y precios de Durable Objects](https://developers.cloudflare.com/durable-objects/platform/pricing/) antes de usarlo con una clase grande.

Para volver a publicar cambios, ejecuta de nuevo `npm run deploy:cloudflare`.

## Ejecutar la versión Node.js en local

```bash
npm install
npm start
```

Abre `http://localhost:3000` y usa una pestaña adicional para simular otro participante.
