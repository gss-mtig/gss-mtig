# Archivos del ejemplo de Sentilo ACA

La aplicación completa usa un servidor Node.js para consultar la API de la ACA y servir el mapa. Descarga estos cuatro archivos y guárdalos juntos en una carpeta local:

- [Servidor Node.js](server.js)
- [Página del mapa](index.html)
- [Carga y normalización de sensores](aca-data.js)
- [Representación Leaflet](aca-map.js)

Desde esa carpeta instala Express e inicia el servidor:

```bash
npm init -y
npm install express
node server.js
```

Abre `http://localhost:3000`. Se necesita conexión a Internet para consultar la API de la ACA y cargar los mapas base.
