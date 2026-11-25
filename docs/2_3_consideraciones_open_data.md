# Evaluar datos y servicios Open Data

Encontrar un conjunto de datos es solo el primer paso. Antes de descargarlo, conectarlo a una API o visualizarlo, conviene comprobar si responde a la pregunta, qué significan sus campos y bajo qué condiciones se puede reutilizar. Una ficha atractiva no garantiza que los datos sean completos, actuales o adecuados para cualquier análisis.

Esta revisión sirve también para decidir si un recurso es apropiado para una aplicación urbana. Una descarga puntual para una práctica tolera tareas manuales que serían problemáticas en un servicio que debe actualizarse cada hora.

## Qué conviene revisar

- **Propósito y cobertura:** qué fenómeno representa el conjunto, qué zona y periodo cubre y qué queda fuera.
- **Calidad y significado:** definición de los campos, unidades, valores ausentes, errores conocidos y método de recopilación.
- **Actualización:** fecha de publicación o última actualización, frecuencia prevista y, si procede, retraso entre el hecho y su publicación.
- **Acceso:** formatos disponibles, posibilidad de descarga y consulta automática, límites de uso, autenticación y estabilidad de las direcciones.
- **Reutilización:** licencia, atribución requerida, condiciones de uso y posibles datos personales o sensibles.
- **Documentación y soporte:** ejemplos de consulta, descripción de respuestas y avisos sobre cambios o interrupciones.

No todas las necesidades exigen una API. Para un análisis puntual puede bastar un archivo descargable. Una aplicación que consulta datos de manera periódica necesita conocer los límites, la frecuencia de actualización, el comportamiento ante errores y las condiciones de acceso.

## Ejemplo de acceso sencillo: feeds del USGS

El [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) publica feeds de terremotos en GeoJSON para distintos periodos y umbrales de magnitud. La documentación identifica el formato, explica que está pensado para su uso por aplicaciones e incluye metadatos en la respuesta, como el título, la fecha de generación, el número de registros y el área cubierta. También publica una [política del ciclo de vida de los feeds](https://earthquake.usgs.gov/earthquakes/feed/v1.0/).

Es un buen ejemplo didáctico de acceso directo: una persona puede abrir una URL en el navegador y obtener una respuesta estructurada que también puede cargar en herramientas compatibles. La documentación y los formatos facilitan probar el servicio y entender qué devuelve. Aun así, antes de usarlo en una aplicación hay que revisar la frecuencia de actualización y la política de cambios; ningún servicio debe considerarse inmutable.

## Ejemplo con fricción de acceso: AEMET OpenData

[AEMET OpenData](https://opendata.aemet.es/) ofrece gratuitamente datos meteorológicos y climatológicos y documenta tanto el acceso general como el acceso para desarrolladores. Para utilizar el servicio se necesita solicitar una API Key. En muchas consultas la API devuelve primero una respuesta con enlaces a los datos y a sus metadatos, que luego hay que solicitar por separado. La [documentación oficial](https://opendata.aemet.es/centrodedescargas/info) explica este flujo y el propósito de la clave.

Esto no convierte al servicio en un mal ejemplo en conjunto: la clave permite identificar y controlar las peticiones y el servicio publica información de uso. Sí añade pasos para quien empieza y obliga a gestionar la clave y el flujo de dos peticiones en una aplicación. Es un caso útil para debatir la diferencia entre que los datos sean gratuitos y reutilizables y que su acceso resulte sencillo para cada tipo de usuario.

### ¿Qué podemos aprender de la comparación?

| Aspecto | USGS Earthquake Feeds | AEMET OpenData |
|---|---|---|
| Primer acceso | URL directa a feeds en varios formatos | Requiere API Key |
| Flujo típico | La respuesta GeoJSON contiene los registros y metadatos | La API puede devolver enlaces que se consultan después |
| Ventaja destacable | Fácil de probar y orientado a aplicaciones | Amplia oferta de datos meteorológicos con documentación y control de peticiones |
| Aspecto que conviene valorar | Vigencia, alcance y política de cambios del feed | Gestión de claves y complejidad adicional del flujo de consulta |

La comparación no establece una clasificación universal. Un servicio con autenticación puede ser apropiado para proteger su disponibilidad, y un acceso directo puede ser insuficiente si los datos carecen de contexto, licencia clara o mantenimiento. La valoración depende del uso previsto.

!!! question "Actividad en clase · 5–10 minutos"

    En parejas, imaginad que queréis representar en **QGIS o ArcGIS** datos de uno de los dos servicios. Localizad en la documentación: **qué datos devuelve**, **cómo se accede**, **qué cobertura temporal tiene** y **si incluye coordenadas o geometrías**. Comentad qué paso adicional necesitaríais para poder analizarlo en un mapa y qué podría limitar o interrumpir su uso. No hace falta entregar la respuesta.

## Lista rápida antes de visualizar

Antes de cargar un conjunto en QGIS, ArcGIS u otra herramienta de análisis o visualización, comprobad al menos:

1. que la cobertura espacial y temporal responde a la pregunta;
2. que entendéis los campos y las unidades, incluidas las coordenadas;
3. que la fecha y la frecuencia de actualización son adecuadas;
4. que la licencia permite el uso previsto;
5. que el archivo o servicio no omite información importante ni presenta errores evidentes.

Una visualización puede hacer visibles patrones y también amplificar sesgos, vacíos o errores de los datos. Interpretad el mapa junto con la documentación del conjunto.

## Para ampliar

- [USGS: feeds de terremotos en GeoJSON (inglés)](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)
- [USGS: documentación de feeds y notificaciones (inglés)](https://earthquake.usgs.gov/earthquakes/feed/v1.0/)
- [AEMET OpenData: información del servicio (español)](https://opendata.aemet.es/centrodedescargas/info)

**Siguiente:** [Visualización con Kepler.gl](4_visualizacion_kepler.md).
