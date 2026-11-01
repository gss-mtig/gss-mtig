# Guía del curso

## Propósito

En este curso estudiaremos cómo localizar, evaluar y consumir datos y geoservicios útiles para aplicaciones de Smart Cities. A partir de servicios reales, veremos cómo llevar esos datos a mapas y cómo valorar sus posibilidades y limitaciones.

El curso complementa la materia de **Infraestructuras de Datos Espaciales (IDES)**. En IDES se estudian con más detalle las infraestructuras, los metadatos y catálogos, los estándares y la publicación de servicios. Aquí nos centraremos en descubrir servicios y usarlos en aplicaciones urbanas.

## Objetivos de aprendizaje

Al finalizar el curso, podrás:

- localizar conjuntos de datos urbanos en portales Open Data y reconocer las opciones de acceso que ofrecen;
- consultar una API de datos abiertos y comprender la estructura básica de su respuesta;
- valorar la documentación, calidad, actualización, cobertura y condiciones de reutilización de un servicio;
- representar datos urbanos en un mapa y reconocer las diferencias entre un archivo y una consulta a una API;
- leer y modificar fragmentos sencillos de HTML y JavaScript para conectar una API y mostrar sus datos en un mapa;
- comparar Leaflet y MapLibre a partir de sus fuentes, capas y posibilidades de estilo;
- reconocer usos de geoservicios de sensores, geocodificación, rutas, isócronas y transporte público;
- explicar las limitaciones de los datos y servicios utilizados en una aplicación.

## Estructura

El curso está organizado en cuatro bloques.

| Bloque                                     | Contenidos                                                                                                  | Ejemplos de aplicación                                              |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **1. Datos urbanos y Open Data**           | Smart Cities, portales de datos abiertos, calidad de datos y consulta mediante APIs.                        | Consulta guiada de una API de Socrata y comparación breve con CKAN. |
| **2. Consumo y representación de datos**   | Consumo de APIs, creación de mapas web y estilos basados en datos.                                            | PMR con Leaflet y Bicing con MapLibre y un mapa base de Vector Tiles. |
| **3. Servicios urbanos y datos dinámicos** | Incidencias ciudadanas, actualización de datos, sensores y limitaciones de los servicios.                   | Caso 311 de Nueva York, movilidad compartida y Sentilo/ACA.         |
| **4. Geoservicios para movilidad**         | Geocodificación, rutas, isócronas y datos de transporte público.                                            | Geocodificadores, GTFS y transporte en tiempo real.                 |

Los casos sirven para aplicar los conceptos. No es necesario completar todos los tutoriales durante las clases; las instrucciones de las prácticas están pensadas para el trabajo autónomo.

## Conocimientos previos

Se recomienda tener conocimientos básicos de información geográfica: qué son las capas, los atributos, las coordenadas y los sistemas de referencia, y cómo visualizar datos en un mapa. También ayuda estar familiarizado con el navegador, los archivos JSON y la edición básica de código. No se presupone experiencia avanzada en programación.

El curso parte de conceptos que se trabajan en IDES. En particular, conviene conocer:

- qué es una IDE y para qué sirven los metadatos y los catálogos;
- qué es un servicio geográfico y cómo se conecta un cliente a un servicio;
- nociones de capas, atributos y coordenadas;
- el uso de un cliente como QGIS o Leaflet.

Si necesitas repasar conceptos de IDE, consulta los materiales de [IDES](https://gss-mtig.github.io/sdis-mgeo/), especialmente [introducción a las IDE](https://gss-mtig.github.io/sdis-mgeo/introduccion_a_las_ides/) y [clientes de mapas](https://gss-mtig.github.io/sdis-mgeo/clientes_de_mapa/).

## Qué se estudia en cada materia

En Geoservicios se usarán datos y APIs para resolver preguntas de aplicación urbana. El objetivo es comprender el flujo desde la consulta de un servicio hasta su representación en un mapa; la explicación detallada de las IDE y los estándares cartográficos se trabaja en la materia de IDES.

## Trabajo práctico

Las prácticas se realizan en casa y amplían las demostraciones de clase. En cada una se indicará qué servicio se consume, qué resultado se espera y qué aspectos de los datos conviene analizar. Además de que el mapa funcione, se tendrá en cuenta que puedas explicar de dónde vienen los datos, cómo se actualizan y qué limitaciones tienen.
