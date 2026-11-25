# 2.1. Consumir datos de un portal Socrata mediante su API

En la página anterior vimos que un portal de datos abiertos puede ofrecer una API. Ahora seguiremos un conjunto de datos desde su ficha en el portal hasta una respuesta que una aplicación puede procesar.

Usaremos el conjunto [311 Service Requests de la ciudad de Nueva York](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9). El servicio 311 recoge avisos y solicitudes de la ciudadanía sobre cuestiones urbanas. Más adelante volveremos a este caso para estudiar su uso como servicio para una Smart City; aquí nos centraremos en cómo consultar datos.

## De la ficha del conjunto a la API

Cada conjunto publicado en Socrata tiene un identificador, que aparece al final de su dirección. En este caso es `erm2-nwe9`. La API de datos de Socrata, llamada SODA, permite consultar los registros de un conjunto mediante una URL.

La dirección base para consultar registros en formato JSON es:

```text
https://data.cityofnewyork.us/resource/erm2-nwe9.json
```

Al abrirla en el navegador se obtiene una respuesta JSON. Para limitar la respuesta a cinco registros, añadimos el parámetro `$limit`:

```text
https://data.cityofnewyork.us/resource/erm2-nwe9.json?$limit=5
```

La URL contiene el dominio del portal (`data.cityofnewyork.us`), el recurso de la API (`/resource/`) y el identificador del conjunto (`erm2-nwe9`). La extensión `.json` indica el formato de respuesta. Los parámetros que siguen a `?` ajustan la consulta.

!!! info "¿Qué significa 311?"
    En varias ciudades de Estados Unidos, el 311 es un canal no urgente para contactar con los servicios municipales. La plataforma registra solicitudes relacionadas, por ejemplo, con residuos, alumbrado o ruido. El conjunto se actualiza y su contenido puede cambiar con el tiempo.

## Elegir campos, filtrar y ordenar

La API permite pedir solo los campos que necesitamos, aplicar condiciones y ordenar los resultados. Socrata utiliza un lenguaje de consulta llamado SoQL, parecido a SQL.

Esta consulta solicita cinco campos, limita la respuesta a cinco registros y los ordena desde los avisos más recientes:

```text
https://data.cityofnewyork.us/resource/erm2-nwe9.json?$select=unique_key,created_date,complaint_type,borough,latitude,longitude&$order=created_date%20DESC&$limit=5
```

En la URL, `%20` representa un espacio. Para filtrar, por ejemplo, los registros de Manhattan, añadimos `$where`:

```text
https://data.cityofnewyork.us/resource/erm2-nwe9.json?$select=unique_key,created_date,complaint_type,borough,latitude,longitude&$where=borough%3D%27MANHATTAN%27&$order=created_date%20DESC&$limit=5
```

Aquí `%3D` representa `=` y `%27` representa una comilla simple. El navegador o una biblioteca cliente suelen encargarse de codificar estos caracteres al construir la petición.

Al examinar la respuesta, podemos reconocer atributos temáticos (`complaint_type`, `borough`) y coordenadas (`latitude`, `longitude`). La presencia de coordenadas permite plantear una representación en un mapa, aunque antes de hacerlo habría que comprobar la calidad y el significado de esos campos.

## Del código a una página que muestra los resultados

Para ver qué ocurre sin tener que programar, abre el [ejemplo interactivo de avisos 311](ejemplos/socrata-311/index.html). Selecciona un distrito y el número de registros, y pulsa **Consultar API**. La página construye una petición, recibe datos del portal y los presenta en una tabla. También permite abrir la URL de la consulta y ver la respuesta JSON original.

También puedes [descargar el archivo HTML completo](ejemplos/socrata-311/index.html){: download="consulta-socrata-311.html"} y abrirlo en un editor de texto para revisar el código. Para probarlo en tu ordenador, sirve el archivo desde un servidor local: abre una terminal en la carpeta donde lo has guardado y ejecuta `python -m http.server 8000` (en algunos equipos, el comando es `python3 -m http.server 8000`). Después abre `http://localhost:8000/consulta-socrata-311.html` en el navegador. Si no tienes Python instalado, puedes probar el [ejemplo publicado](ejemplos/socrata-311/index.html).

!!! info "Qué observar"
    Al cambiar el distrito o el número de registros, cambia la petición que se envía. La tabla muestra los datos que devuelve la API; no son datos escritos previamente en la página.

El bloque siguiente contiene **el archivo HTML completo**: estructura de la página, estilos y JavaScript. Puedes copiarlo en un archivo llamado `consulta-socrata-311.html` y ejecutarlo con el servidor local indicado arriba. La llamada a la API está en la parte final, dentro de la etiqueta `<script>`.

!!! info "Código completo de la página"

    ```html
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Consulta de avisos 311 | Ejemplo de API Socrata</title>
      <style>
        :root { color-scheme: light; font-family: system-ui, sans-serif; color: #182230; background: #f3f6f8; }
        body { margin: 0; }
        main { max-width: 980px; margin: 2rem auto; padding: 0 1rem; }
        .panel { background: white; border: 1px solid #d8e0e7; border-radius: 12px; padding: 1.25rem; margin: 1rem 0; }
        h1 { margin-bottom: .4rem; font-size: clamp(1.6rem, 4vw, 2.2rem); }
        h2 { font-size: 1.2rem; margin-top: 0; }
        p { line-height: 1.55; }
        .controls { display: flex; flex-wrap: wrap; gap: 1rem; align-items: end; }
        label { display: grid; gap: .35rem; font-weight: 650; }
        select, button { font: inherit; padding: .65rem .8rem; border: 1px solid #8998a7; border-radius: 6px; background: white; }
        button { color: white; background: #075985; border-color: #075985; cursor: pointer; font-weight: 700; }
        button:hover { background: #0c4a6e; }
        button:focus-visible, select:focus-visible, a:focus-visible { outline: 3px solid #f59e0b; outline-offset: 2px; }
        #status { min-height: 1.5rem; }
        .table-wrap { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: .94rem; }
        th, td { border-bottom: 1px solid #d8e0e7; padding: .7rem .55rem; text-align: left; vertical-align: top; }
        th { background: #eef3f6; }
        code { overflow-wrap: anywhere; }
        .small { color: #4a5968; font-size: .92rem; }
      </style>
    </head>
    <body>
      <main>
        <h1>Avisos ciudadanos 311 de Nueva York</h1>
        <p>Esta página consulta el conjunto público de solicitudes municipales 311 mediante la API de Socrata y presenta algunos registros en una tabla.</p>

        <section class="panel" aria-labelledby="controls-title">
          <h2 id="controls-title">Configura la consulta</h2>
          <div class="controls">
            <label for="borough">Distrito
              <select id="borough">
                <option value="">Todos</option>
                <option value="MANHATTAN" selected>Manhattan</option>
                <option value="BROOKLYN">Brooklyn</option>
                <option value="QUEENS">Queens</option>
                <option value="BRONX">Bronx</option>
                <option value="STATEN ISLAND">Staten Island</option>
              </select>
            </label>
            <label for="limit">Número de registros
              <select id="limit">
                <option>5</option>
                <option>10</option>
                <option>20</option>
              </select>
            </label>
            <button id="search" type="button">Consultar API</button>
          </div>
          <p id="status" role="status" aria-live="polite">Preparando la consulta…</p>
          <p class="small">La respuesta muestra como máximo el número de registros elegido, ordenados por fecha de creación más reciente.</p>
        </section>

        <section class="panel" aria-labelledby="results-title">
          <h2 id="results-title">Resultados recibidos</h2>
          <div class="table-wrap">
            <table>
              <thead>
                <tr><th>Fecha</th><th>Tipo de aviso</th><th>Distrito</th><th>Coordenadas</th><th>Identificador</th></tr>
              </thead>
              <tbody id="resultados"></tbody>
            </table>
          </div>
        </section>

        <section class="panel">
          <h2>La petición a la API</h2>
          <p>La página construye una URL con los campos, el filtro y el límite seleccionados. Puedes abrir esa URL para ver la respuesta JSON original:</p>
          <p><a id="api-link" href="https://data.cityofnewyork.us/resource/erm2-nwe9.json?$limit=5" target="_blank" rel="noopener">Abrir la consulta JSON</a></p>
          <p class="small">Fuente: <a href="https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9" target="_blank" rel="noopener">NYC Open Data · 311 Service Requests</a>.</p>
        </section>
      </main>

      <script>
        const endpoint = "https://data.cityofnewyork.us/resource/erm2-nwe9.json";
        const fields = "unique_key,created_date,complaint_type,borough,latitude,longitude";
        const boroughSelect = document.querySelector("#borough");
        const limitSelect = document.querySelector("#limit");
        const status = document.querySelector("#status");
        const results = document.querySelector("#resultados");
        const apiLink = document.querySelector("#api-link");

        function buildRequestUrl() {
          const url = new URL(endpoint);
          url.searchParams.set("$select", fields);
          if (boroughSelect.value) {
            url.searchParams.set("$where", `borough = '${boroughSelect.value}'`);
          }
          url.searchParams.set("$order", "created_date DESC");
          url.searchParams.set("$limit", limitSelect.value);
          return url;
        }

        function addCell(row, value) {
          const cell = document.createElement("td");
          cell.textContent = value || "Sin dato";
          row.append(cell);
        }

        async function loadRecords() {
          const url = buildRequestUrl();
          apiLink.href = url.href;
          results.replaceChildren();
          status.textContent = "Consultando el portal de datos…";

          try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`Error HTTP ${response.status}`);
            const records = await response.json();

            for (const record of records) {
              const row = document.createElement("tr");
              const coordinates = record.latitude && record.longitude
                ? `${record.latitude}, ${record.longitude}`
                : "Sin coordenadas";
              addCell(row, record.created_date);
              addCell(row, record.complaint_type);
              addCell(row, record.borough);
              addCell(row, coordinates);
              addCell(row, record.unique_key);
              results.append(row);
            }

            status.textContent = records.length
              ? `La API ha devuelto ${records.length} registros.`
              : "La consulta no ha devuelto registros. Prueba otro distrito.";
          } catch (error) {
            status.textContent = `No se pudieron cargar los datos: ${error.message}. Comprueba tu conexión e inténtalo de nuevo.`;
          }
        }

        document.querySelector("#search").addEventListener("click", loadRecords);
        loadRecords();
      </script>
    </body>
    </html>
    ```

`fetch` realiza la petición HTTP; `response.json()` convierte la respuesta en registros; y el código crea una fila de tabla por cada registro. `URL` y `searchParams` construyen la dirección y codifican los parámetros. Los controles de distrito y límite modifican esos parámetros antes de cada petición.

!!! question "Prueba rápida en clase (5–10 min)"
    Abre el ejemplo interactivo. Cambia el distrito y el número de registros y observa cómo se actualizan la tabla y el enlace a la consulta JSON. ¿Qué campos usarías para distinguir una solicitud de otra y cuáles necesitarías para situarla en un mapa?

## Aspectos que conviene comprobar

- **Identificador y ficha:** confirma que la API corresponde al conjunto de datos que quieres utilizar.
- **Campos disponibles:** los nombres y tipos de campo condicionan las consultas y el análisis.
- **Cobertura y actualización:** revisa el periodo, la frecuencia de actualización y las limitaciones descritas en el portal.
- **Coordenadas:** comprueba si hay valores vacíos, si representan el lugar del incidente o una aproximación, y qué sistema de referencia se utiliza.
- **Límites de uso:** para consultas sencillas, Socrata permite peticiones sin token; una aplicación con uso frecuente debería registrarse y utilizar un token. No incluyas credenciales privadas en código público del navegador.

!!! note "Para ampliar"
    La página siguiente ofrece una comparación breve con CKAN. Es opcional: el objetivo principal de esta unidad es entender el flujo entre la ficha de un conjunto, su endpoint y una respuesta de datos.

## Referencias

- [Conjunto 311 de NYC Open Data](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9)
- [Guía de inicio para consumir la API SODA (inglés)](https://dev.socrata.com/consumers/getting-started.html)
- [Consultas con SoQL (inglés)](https://dev.socrata.com/docs/queries/)
- [Tokens de aplicación y límites de uso (inglés)](https://dev.socrata.com/docs/app-tokens.html)

**Siguiente:** [CKAN (opcional)](2_2_api_ckan_opcional.md).
