# Elegir herramientas para visualizar datos geográficos

Hay herramientas para tareas distintas. Algunas son bibliotecas de JavaScript con las que se construyen mapas web; otras permiten explorar datos o publicar mapas sin escribir una aplicación desde cero. La elección depende del resultado que buscamos, de los datos disponibles y de cuánto código queremos mantener.

## Bibliotecas para crear mapas web

| Herramienta | Cuándo puede resultar útil | Ejemplo o referencia del curso |
|---|---|---|
| [Leaflet](https://leafletjs.com/) | Crear mapas web interactivos con una API accesible y un ecosistema amplio de extensiones. Es una buena opción para aprender las piezas básicas de un mapa web. | Se usa en los ejemplos de [Zaragoza PMR](8_ejemplo_parking_movilidad_reducida_zaragoza.md) y [Sentilo ACA](12_ejemplo_sentilo_aca.md). |
| [OpenLayers](https://openlayers.org/) | Crear aplicaciones cartográficas con varias fuentes, formatos y tipos de capas. Es una biblioteca amplia y flexible, adecuada cuando el proyecto necesita combinar distintos servicios y datos geográficos. | [Documentación y ejemplos oficiales de OpenLayers](https://openlayers.org/doc/). |
| [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/) | Crear mapas interactivos con estilos detallados y teselas vectoriales. Permite personalizar la representación y modificarla según los atributos de los datos. | Se usa en [Bicing con MapLibre](10_ejemplo_servicio_bicing_bcn_vt.md). |

Leaflet, OpenLayers y MapLibre son bibliotecas: ofrecen componentes para construir una aplicación, pero quien desarrolla decide qué datos cargar, cómo mostrarlos y cómo responder a las interacciones. No son portales de datos ni sustituyen al servicio que entrega la información.

## Herramientas para explorar o publicar mapas

| Tipo de herramienta | Para qué sirve | Ejemplo del curso |
|---|---|---|
| Exploración visual | Probar una visualización rápidamente y explorar patrones sin crear una aplicación web completa. | [Kepler.gl](4_visualizacion_kepler.md). |
| Plataformas web de mapas | Crear, alojar o compartir mapas mediante una interfaz web. Las funciones disponibles, los formatos admitidos y las condiciones de uso dependen de cada plataforma. | [Instamaps del ICGC](https://www.instamaps.cat/). |
| Sistemas de información geográfica de escritorio | Preparar, consultar y analizar datos antes de publicarlos o incorporarlos a una aplicación web. | QGIS y ArcGIS, que el alumnado ya conoce. |

Estas categorías pueden combinarse. Por ejemplo, se puede revisar un archivo en QGIS, explorar su distribución en Kepler.gl y después construir una aplicación con Leaflet, OpenLayers o MapLibre. La decisión también depende de si la visualización debe ser un análisis puntual, un mapa para compartir o una aplicación que consuma datos actualizados.

## Comparar antes de elegir

Antes de empezar, responde estas preguntas:

1. ¿Necesito explorar un conjunto de datos o construir una aplicación para otras personas?
2. ¿Los datos vienen de un archivo, una API, un servicio cartográfico o teselas vectoriales?
3. ¿Necesito actualizar los datos, mostrar cambios temporales o permitir que el usuario interactúe con ellos?
4. ¿Qué conocimientos de código, alojamiento y mantenimiento requiere la opción elegida?
5. ¿Hay límites de uso, claves, atribuciones o condiciones de licencia que deba considerar?

En este curso usaremos Kepler.gl para explorar datos, Leaflet para construir mapas web paso a paso y MapLibre para ver estilos y teselas vectoriales. OpenLayers queda como alternativa relevante para conocer y comparar: no hace falta aprender las tres bibliotecas en detalle en estas 16 horas. La materia de IDES profundiza en la publicación y los estándares de servicios geográficos.

!!! question "Prueba breve en clase · 5–10 minutos"

    Para cada tarea, elegid una herramienta y justificad la elección en una frase: **explorar rápidamente miles de puntos de un CSV**, **hacer un mapa sencillo que consulte una API** y **crear un mapa con estilo basado en teselas vectoriales**. Después, comentad qué cambiaría si el mapa tuviera que actualizarse automáticamente cada minuto.

## Para ampliar

- [Leaflet: referencia de la API (inglés)](https://leafletjs.com/reference.html)
- [OpenLayers: documentación oficial (inglés)](https://openlayers.org/doc/)
- [MapLibre GL JS: documentación oficial (inglés)](https://maplibre.org/maplibre-gl-js/docs/)
- [Kepler.gl: documentación oficial (inglés)](https://docs.kepler.gl/)
- [Instamaps del ICGC](https://www.instamaps.cat/)

**Siguiente:** [Geocodificación con OpenCage](15_ejemplo_geocodificador.md).
