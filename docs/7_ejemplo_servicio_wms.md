# Ejemplo servicio WMS

## Acceso al servicio WMS

La manera más fácil de encontrar las url de los servicios WMS es buscando en la IDE correspondiente o si conocemos al proveedor del servicio buscando en su página web.

En el portal del [PNOA](https://pnoa.ign.es/) podemos encontrar los diferentes productos y servicios que ofrece. Otro ejemplo también sería la web del [Institut Cartogràfic i Geològic de Catalunya (ICGC)](https://icgc.cat/Administracio-i-empresa/Serveis/Geoinformacio-en-linia-Geoserveis) 

La url del servicio WMS de Ortofotos del PNOA es: http://www.ign.es/wms-inspire/pnoa-ma?request=GetCapabilities&service=WMS

Para ver las capacidades y descripción del servicio tenemos que hacer una consulta GetCapabilities http://www.ign.es/wms-inspire/pnoa-ma?request=GetCapabilities&service=WMS. Al abrir la consulta en nuestro navegador vemos un XML donde se describe el servicio y donde podremos sacar los parámetros necesarios para poder visualizar el servicio en nuestro visor de mapas.

Para ver los datos de este servicio sobre un mapa crearemos un visor utilizando Leaflet. [^1]

## Creación de un visor

- Crear una carpeta con el nombre de *visor-wms*.
- Crear un archivo con el nombre de *index.html* dentro de la carpeta
- Abrir el archivo index.html con un editor de texto y copiar el siguiente código.

```html
<!DOCTYPE html>
<html>
<head>
  <title>Servicio de WMS</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
  <style>
    #mapid {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    }
  </style>
</head>
<body>
  <div id="mapid"></div>

  <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
  <script type="text/javascript">
    var map = L.map('mapid');
    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  </script>
</body>
</html>
```

- Abrir el archivo index.html en el navegador para ver que carga un mapa centrado en Barcelona.

- Agregar la capa WMS del PNOA

```html hl_lines="32 33 34 35 36 37 38"
<!DOCTYPE html>
<html>
<head>
  <title>Servicio de WMS</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
  <style>
    #mapid {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    }
  </style>
</head>
<body>
  <div id="mapid"></div>

  <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
  <script type="text/javascript">
    var map = L.map('mapid');
    map.setView([41.3887, 2.1777], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var pnoa = L.tileLayer.wms("http://www.ign.es/wms-inspire/pnoa-ma?SERVICE=WMS&", {
      layers: 'OI.OrthoimageCoverage',
      format: 'image/png',
      transparent: true,
      version: '1.3.0',//wms version (ver get capabilities)
      attribution: "PNOA WMS. Cedido por © Instituto Geográfico Nacional de España"
    }).addTo(map);

  </script>
</body>
</html>
```

- Recargar la página para visualizar nuestra capa WMS de Ortofotos.

!!! question "Ejercicio"
	  Agregar el servicio WMS de Ortofotos del ICGC. URL del servicio http://geoserveis.icc.cat/icc_mapesmultibase/noutm/wms/service?
    
    Para ver el nombre de la capa (layers) hacer un GetCapabilities http://geoserveis.icc.cat/icc_mapesmultibase/noutm/wms/service?SERVICE=WMS&VERSION=1.3.0&REQUEST=Getcapabilities.
    
    En el parámetro attribution de la nueva capa poner "Institut Cartogràfic i Geològic de Catalunya"


## Referencias
[^1]: http://leafletjs.com/