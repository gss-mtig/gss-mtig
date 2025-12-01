# Ejemplo servicio aparcamientos PMR Zaragoza

## Acceso al servicio de datos del Ayuntamiento de Zaragoza

En el [Portal de Datos Abiertos del Ayuntamiento de Zaragoza](https://www.zaragoza.es/sede/portal/datos-abiertos/) podemos encontrar una gran cantidad de servicios de smart city, entre ellos los relacionados con urbanismo, movilidad y medio ambiente.

El servicio que utilizaremos en este ejemplo es el de Aparcamientos para Personas con Discapacidad, disponible en el endpoint:

https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/equipamiento/aparcamiento-personas-discapacidad

Al acceder, el servicio devuelve un XML con información sobre los puntos de estacionamiento reservados a personas con movilidad reducida, incluyendo las coordenadas, dirección, tipo y un icono asociado.

## Creación de un visor

- Crear una carpeta con el nombre de *visor-aparcamientos-pmr*.
- Crear un archivo con el nombre de *index.html* dentro de la carpeta
- Abrir el archivo index.html con un editor de texto y copiar el siguiente código.

```html
<!DOCTYPE html>
<html>
<head>
  <title>Aparcamientos PMR Zaragoza</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <style>
    #map {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script>
    const map = L.map('map').setView([41.65, -0.88], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
  </script>
</body>
</html>
```

- Guarda y abre el archivo index.html en el navegador. Deberías ver un mapa centrado en Zaragoza.

## Consultar la API del Ayuntamiento

Aqui podemos ver y probar la API: https://www.zaragoza.es/docs-api_sede/#/Equipamientos%20y%20movilidad%3A%20Aparcamientos%20para%20personas%20con%20discapacidad

La API permite obtener los datos con un fetch añadiendo parámetros, por ejemplo para limitar a 50 registros:

https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/equipamiento/aparcamiento-personas-discapacidad?rf=html&start=0&rows=50

El servidor exige que el encabezado Accept sea `application/json`.
Por tanto, haremos la llamada con este encabezado.

Agrega el siguiente código al final de tu `<script>`:

```html hl_lines="27-37"
<!DOCTYPE html>
<html>
<head>
  <title>Aparcamientos PMR Zaragoza</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <style>
    #map {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script>
    const map = L.map('map').setView([41.65, -0.88], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const url = 'https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/equipamiento/aparcamiento-personas-discapacidad?rf=html&start=0&rows=50';

    fetch(url, {
      headers: {
        'Accept': 'application/json'
      }
    })
    .then(res => res.json())
    .then(data => {
      console.log(data);
    });
  </script>
</body>
</html>
```

- Abre la consola del navegador (F12 → pestaña Console) y verás los datos descargados.

## Mostrar los aparcamientos sobre el mapa

Cada registro contiene coordenadas en el campo geometry.coordinates.
Crearemos un marcador por cada uno.

Añade debajo del console.log(data) lo siguiente:

```html hl_lines="37-60"
<!DOCTYPE html>
<html>
<head>
  <title>Aparcamientos PMR Zaragoza</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
  <style>
    #map {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script>
    const map = L.map('map').setView([41.65, -0.88], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const url = 'https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/equipamiento/aparcamiento-personas-discapacidad?rf=html&start=0&rows=50';

    fetch(url, {
      headers: {
        'Accept': 'application/json'
      }
    })
    .then(res => res.json())
    .then(data => {
      console.log(data);
      // Icono personalizado (usa un icono de silla de ruedas libre)
      const iconUrl = 'https://www.svgrepo.com/show/277/parking-for-disabled-persons-sign.svg';
      const pmrIcon = L.icon({
        iconUrl,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
      });

      // Recorrer los resultados
      data.result.forEach(p => {
        if (!p.geometry || !p.geometry.coordinates) return;

        const [lon, lat] = p.geometry.coordinates;

        const marker = L.marker([lat, lon], { icon: pmrIcon }).addTo(map);

        marker.bindPopup(`
          <strong>${p.tipo_reserva}</strong><br>
          Dirección: ${p.calle_1 || 'Desconocida'}, ${p.num_calle1 || 'S/N'}<br>
          Categoria: ${p.categoria || 'N/D'}<br>
          Plazas: ${p.plazas || 'N/D'}
        `);
      });
    });
  </script>
</body>
</html>
```

- Guarda y recarga la página. Ahora deberías ver los puntos de aparcamiento PMR sobre el mapa, cada uno con su icono y popup.
