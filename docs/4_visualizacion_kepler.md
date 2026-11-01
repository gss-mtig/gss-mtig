# Visualización exploratoria con Kepler.gl

[Kepler.gl](https://kepler.gl/) es una aplicación web para explorar datos con componente geográfica. Permite cargar archivos como CSV o GeoJSON, crear capas de visualización y explorar patrones espaciales y temporales desde el navegador. No hace falta programar para construir un mapa.

En esta sesión nos centraremos en una pregunta sencilla: **¿cómo cambia la distribución de accidentes de tráfico de Barcelona cuando agrupamos los puntos en hexágonos?** La visualización sirve para explorar los datos y formular preguntas; por sí sola no explica por qué ocurren los accidentes ni mide el riesgo.

## Preparar los datos

Usaremos el archivo anual de 2024 del conjunto [Accidentes gestionados por la Guardia Urbana en Barcelona](https://opendata-ajuntament.barcelona.cat/data/es/dataset/accidents-gu-bcn). El [CSV de 2024](https://opendata-ajuntament.barcelona.cat/data/dataset/e769eb9d-d778-4cd7-9e3a-5858bba49b20/resource/66f5e7e3-045b-4d19-b649-2eaea622ae93/download) contiene la localización de los accidentes y otros atributos. Elegimos un año completo para comparar el mismo periodo temporal.

Antes de cargar un archivo, conviene comprobar:

- que la tabla tiene una fila de encabezados y una fila por registro;
- que las columnas `Latitud_WGS84` y `Longitud_WGS84` contienen coordenadas en grados decimales;
- que la latitud y la longitud no están intercambiadas y no hay valores vacíos o incorrectos;
- qué periodo cubren los datos y cuándo se actualizaron.

Kepler.gl trabaja con coordenadas geográficas WGS84. Al crear una capa de puntos o hexágonos, la latitud corresponde al eje norte-sur y la longitud al eje este-oeste. Si los nombres de las columnas no se reconocen automáticamente, se pueden asignar manualmente en la configuración de la capa.

## Crear una visualización

1. Descarga el CSV de 2024 desde la ficha de Open Data BCN.
2. Abre [Kepler.gl Demo](https://kepler.gl/demo) y carga el archivo CSV desde tu ordenador.
3. En **Layers**, añade una capa de tipo **Hexagon**.
4. Selecciona `Latitud_WGS84` como latitud y `Longitud_WGS84` como longitud.
5. Ajusta el radio de los hexágonos y el color. La altura es opcional.
6. Acerca el mapa y compara las zonas con más y menos registros agregados.

Una capa de **puntos** muestra la ubicación de cada registro; una capa de **hexágonos** agrupa los puntos en celdas y permite representar el número de accidentes por zona. El tamaño de celda cambia la lectura: celdas grandes suavizan el detalle y celdas pequeñas muestran más variación local.

!!! info "Interpretar el mapa con cuidado"
    Un hexágono con más puntos indica más accidentes registrados dentro de esa celda en el periodo analizado. No significa necesariamente que ese lugar tenga más riesgo: para comparar riesgos habría que considerar, entre otros factores, el volumen de tráfico, la población expuesta, la gravedad de los accidentes y la calidad de las coordenadas. Los accidentes registrados tampoco equivalen a todos los incidentes ocurridos.

!!! exercise "Prueba breve en clase · 5–10 minutos"

    Cambia el radio de los hexágonos y observa cómo se modifica el patrón. Después, activa una capa de puntos o cambia el color para representar otra variable disponible, como el número de víctimas. Comentad: ¿qué patrón se mantiene y cuál depende de la forma de agrupar los datos? No hace falta entregar el ejercicio.

## Guardar o compartir el resultado

Kepler.gl procesa los archivos cargados en el navegador. La aplicación de demostración indica que los datos permanecen en el equipo y no se envían a sus servidores. Desde el menú de exportación se puede guardar una imagen o exportar el mapa y los datos filtrados. Si compartes una visualización, comprueba qué información contiene y si está permitido publicarla.

## Referencias

- [Kepler.gl: guía para empezar (inglés)](https://docs.kepler.gl/docs/user-guides/j-get-started)
- [Cargar datos en Kepler.gl (inglés)](https://docs.kepler.gl/docs/user-guides/b-kepler-gl-workflow/a-add-data-to-the-map)
- [Crear capas de visualización (inglés)](https://docs.kepler.gl/docs/user-guides/b-kepler-gl-workflow/add-data-to-layers/b-create-a-layer)
- [Capa Hexbin: agregación de puntos en hexágonos (inglés)](https://docs.kepler.gl/docs/user-guides/c-types-of-layers/h-hexbin)
- [Exportar datos e imágenes (inglés)](https://docs.kepler.gl/docs/user-guides/k-save-and-export)
- [Ficha del conjunto de accidentes en Open Data BCN](https://opendata-ajuntament.barcelona.cat/data/es/dataset/accidents-gu-bcn)
- [Metadatos del conjunto en datos.gob.es (español)](https://datos.gob.es/es/catalogo/l01080193-accidentes-gestionados-por-la-guardia-urbana-en-la-ciudad-de-barcelona)
