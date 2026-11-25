# Herramientas para visualizar datos

La herramienta adecuada depende de la pregunta, de quién va a usar el resultado y de cómo se actualizarán los datos. No es lo mismo explorar puntos sobre un mapa, crear un gráfico para una página web o mantener un panel de seguimiento para un equipo municipal.

En la página anterior usamos **Kepler.gl** para explorar datos geográficos sin programar. Aquí ampliaremos el panorama y distinguiremos tres familias: herramientas de exploración geográfica, bibliotecas para crear visualizaciones web y plataformas de inteligencia de negocio.

## Elegir según el objetivo

| Necesidad | Herramienta que puede encajar | Qué tener en cuenta |
|---|---|---|
| Explorar ubicaciones y patrones espaciales o temporales en un CSV o GeoJSON | **Kepler.gl** | Permite crear mapas interactivos desde archivos con poca o ninguna programación. Ya lo hemos probado con una capa de hexágonos. |
| Añadir gráficos a una aplicación o página web propia | **Chart.js** | Adecuado para gráficos habituales, como barras o líneas. Hay que trabajar con HTML y JavaScript. |
| Describir gráficos interactivos mediante una especificación | **Vega-Lite** | Usa una estructura declarativa en JSON para indicar datos, marcas visuales y relaciones entre campos. Requiere aprender esa sintaxis. |
| Crear una visualización web muy personalizada | **D3.js** | Ofrece gran flexibilidad, pero exige más conocimientos de programación y diseño web. |
| Explorar datos, construir informes y compartir paneles dentro de una organización | **Herramientas de BI**, como Power BI, Tableau o Qlik | Suelen ofrecer interfaces visuales para modelar datos y crear informes. Hay que revisar conectores, opciones de publicación, licencias y dónde se alojan los datos. |

Estas categorías se solapan. Por ejemplo, una plataforma de BI puede incluir mapas, y una biblioteca web puede generar gráficos interactivos. La tabla sirve como orientación inicial, no como clasificación rígida ni como recomendación de una marca concreta.

## Bibliotecas y plataformas: dos formas de trabajar

Una **biblioteca de visualización** es un componente que se incorpora a un programa. El equipo de desarrollo decide cómo se cargan los datos, cómo se representa cada campo y cómo se integra el gráfico en la aplicación. Esto ofrece control, pero requiere programación y mantenimiento.

Una **plataforma de inteligencia de negocio (BI)** reúne funciones para conectar fuentes, preparar o modelar datos, crear informes y compartirlos. Puede reducir la cantidad de código que se escribe, pero no elimina la necesidad de entender los datos, mantener las conexiones ni decidir quién puede verlos. También puede haber restricciones de licencia, publicación y almacenamiento.

Kepler.gl ocupa otro lugar: es una aplicación de exploración geográfica preparada para crear mapas a partir de archivos compatibles. En la práctica anterior hemos visto cómo cargar un CSV y configurar una capa. No sustituye necesariamente a un sistema de informes que se actualiza de forma periódica ni a una biblioteca integrada en una aplicación propia.

## Preguntas para escoger una herramienta

Antes de empezar, conviene responder:

1. **¿Qué pregunta debe ayudar a responder la visualización?** Comparar categorías, ver cambios en el tiempo, explorar ubicaciones o comunicar un indicador.
2. **¿Quién la usará y qué podrá hacer?** Consultar un resultado fijo, filtrar datos o explorar distintas vistas.
3. **¿Dónde debe funcionar?** En un archivo local, en una aplicación web, en un informe interno o en un portal público.
4. **¿Cómo se actualizan los datos?** Una imagen estática puede bastar para un análisis puntual; un panel operativo necesita una fuente y un proceso de actualización mantenidos.
5. **¿Qué conocimientos y condiciones hay disponibles?** Programación, presupuesto, licencias, alojamiento, accesibilidad y privacidad.

Una herramienta sofisticada no corrige datos incompletos ni una pregunta mal planteada. Conviene revisar primero la calidad, la cobertura y el significado de los datos, y luego escoger la forma de mostrarlos.

!!! exercise "Prueba breve en clase · 5–10 minutos"

    Para cada caso, elegid una de las familias de la tabla y justificad la decisión con una ventaja y una limitación:

    - Un equipo quiere explorar dónde se concentran las incidencias municipales registradas durante un año.
    - Un ayuntamiento quiere consultar cada mañana un panel interno con indicadores de servicio.
    - Un grupo quiere incorporar un gráfico de evolución mensual en una aplicación web propia.

    No hace falta entregar la respuesta. Si dos herramientas os parecen válidas, explicad qué condición os haría elegir entre ellas.

## Para ampliar

- [Chart.js: guía de inicio (inglés)](https://www.chartjs.org/docs/latest/getting-started/)
- [Vega-Lite: documentación y ejemplos (inglés)](https://vega.github.io/vega-lite/)
- [D3.js: qué es D3 (inglés)](https://d3js.org/what-is-d3)
- [Documentación de introducción a Power BI (español)](https://learn.microsoft.com/es-es/power-bi/fundamentals/)
- [Aprender a usar Tableau (español)](https://www.tableau.com/es-es/learn)
- [Visualizaciones en Qlik Cloud (español)](https://help.qlik.com/es-ES/cloud-services/Subsystems/Hub/Content/Sense_Hub/Visualizations/visualizations-visualizing-data.htm)
- [Guía de Kepler.gl: cargar datos (inglés)](https://docs.kepler.gl/docs/user-guides/b-kepler-gl-workflow/a-add-data-to-the-map)

**Siguiente:** [API municipal y mapa web: aparcamientos PMR de Zaragoza](8_ejemplo_parking_movilidad_reducida_zaragoza.md).
