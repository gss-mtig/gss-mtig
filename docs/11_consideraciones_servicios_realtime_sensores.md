# Sensores urbanos: SOS, Sentilo y calidad de los datos

Los sensores permiten observar fenómenos que cambian con el tiempo: nivel de agua, caudal de un río, ruido, calidad del aire o temperatura. Para interpretar una medida no basta con su valor. También hacen falta, como mínimo, la propiedad observada, la unidad, la ubicación, la fecha y hora de la observación y una referencia al sensor o método que la produjo.

Una medición sin contexto puede llevar a conclusiones incorrectas. Por ejemplo, `18` podría representar 18 °C, 18 mm de lluvia o un nivel de agua en otra unidad; sin fecha tampoco sabemos si describe la situación actual.

## SOS: una interfaz OGC para consultar observaciones

**SOS** significa *Sensor Observation Service*. Es un estándar de interfaz del Open Geospatial Consortium (OGC) para consultar observaciones, metadatos de sensores y los elementos observados. En SOS 2.0, las operaciones principales incluyen `GetCapabilities` —qué ofrece el servicio—, `DescribeSensor` —información del sensor— y `GetObservation` —consulta de observaciones—. El estándar también contempla operaciones para registrar sensores e insertar observaciones.

El objetivo es que diferentes clientes puedan consultar servicios con una interfaz común, aunque procedan de distintos proveedores. El estándar no garantiza por sí solo que todos los datos sean comparables ni correctos: también hay que revisar las unidades, los metadatos, la calidad de las medidas y qué partes del estándar implementa cada servicio. Los detalles de SOS y de los estándares OGC se trabajarán en la materia de IDES.

## ¿SensorThings API sustituye a SOS?

La [OGC SensorThings API](https://ogcapi.ogc.org/sensorthings/) ofrece funciones parecidas a SOS —consultar sensores, metadatos y observaciones—, pero adopta un diseño pensado para dispositivos IoT y aplicaciones web: recursos REST, consultas con convenciones OData y respuestas JSON. Por ejemplo, la API organiza la información en recursos como `Things`, `Datastreams`, `Sensors` y `Observations`.

No es correcto decir que SensorThings haya reemplazado formalmente a SOS. El OGC mantiene ambos como estándares publicados. SensorThings es una alternativa más reciente para ciertos usos, mientras que SOS sigue siendo válido en servicios y flujos que ya lo implementan.

El estándar más reciente de esta familia es **OGC API – Connected Systems** (versión 1.0, publicada en 2025). Moderniza capacidades de la arquitectura Sensor Web Enablement mediante APIs REST/OpenAPI y relaciona los sistemas y sus metadatos con datos dinámicos como las observaciones. El propio OGC indica que puede integrarse con SensorThings; por eso conviene entenderlo como una vía de modernización más amplia, no como una migración automática de todos los servicios SOS o SensorThings existentes.

| Estándar | Idea principal |
|---|---|
| SOS | Interfaz OGC para consultar observaciones y metadatos de sensores; habitual en arquitecturas SWE existentes. |
| SensorThings API | API OGC REST para conectar dispositivos IoT, datos y aplicaciones web, con recursos y consultas JSON/OData. |
| OGC API – Connected Systems | API OGC más reciente para describir sistemas conectados y acceder a sus datos dinámicos; moderniza capacidades SWE y puede enlazarse con SensorThings. |

## Servicios y ejemplos SensorThings

La [API de sensores de Hamburgo](https://iot.hamburg.de/v1.1/) es un servicio público SensorThings versión 1.1 incluido en el [directorio de endpoints públicos del OGC](https://github.com/opengeospatial/sensorthings/blob/master/PublicEndPoints.md), bajo el apartado Smart Cities. Al abrir la raíz de la API se muestran sus recursos; se puede seguir `Things`, `Datastreams` y `Observations` para explorar dispositivos, flujos de medidas y observaciones.

Como ejemplo de aire, Fraunhofer ofrece la [API SensorThings de calidad del aire europea](https://airquality-frost.k8s.ilt-dmz.iosb.fraunhofer.de/v1.1/) y un [visor WebGenesis](https://api4inspire.k8s.ilt-dmz.iosb.fraunhofer.de/servlet/is/127/) conectado a ese servicio. Para revisar cómo llevar datos SensorThings a un mapa web, [STAM (SensorThings API Map)](https://github.com/DataCoveEU/STAM) incluye ejemplos de código con Leaflet y OpenLayers; hay que configurar la dirección de una API compatible antes de ejecutar el ejemplo.

## Sentilo: plataforma para compartir datos de sensores

[Sentilo](https://www.sentilo.io/) es una plataforma de código abierto impulsada inicialmente por el Ayuntamiento de Barcelona para integrar datos de sensores y actuadores en proyectos de ciudad. Ofrece un catálogo y una API REST para publicar, consultar y distribuir datos; las aplicaciones pueden recibir datos mediante suscripciones y enviar órdenes a dispositivos autorizados.

En su modelo, un **proveedor** agrupa dispositivos; un **componente** representa un equipo o elemento geolocalizado, y uno o varios **sensores** producen observaciones asociadas a ese componente. El catálogo describe esos elementos y ayuda a conocer qué datos están disponibles.

Sentilo es una plataforma con su propia API, no una implementación de SOS. Que una API use HTTP y JSON no significa que sea SOS ni que sus respuestas sean GeoJSON. Para representar sus observaciones en un mapa puede ser necesario interpretar el catálogo, comprobar la estructura de las medidas y transformar las ubicaciones y atributos al formato que espere la herramienta cartográfica.

La [Agencia Catalana del Agua (ACA)](https://aca.gencat.cat/ca/laigua/consulta-de-dades/dades-obertes/dades-obertes-temps-real/) utiliza Sentilo para publicar datos de embalses, aforos, pluviómetros y piezómetros. Ofrece un visor, un catálogo y una API REST. La API devuelve JSON; el ejemplo de la lección siguiente muestra cómo leer su catálogo y transformar ubicaciones para crear un mapa.

## Buenas prácticas al publicar y consumir datos

### Buenas prácticas de publicación

La página de [datos abiertos en tiempo real de la ACA](https://aca.gencat.cat/ca/laigua/consulta-de-dades/dades-obertes/dades-obertes-temps-real/) es un ejemplo útil porque reúne enlaces al visor, al catálogo y a las consultas de datos, y enlaza un [manual de uso de la API](https://aca.gencat.cat/web/.content/20_Aigua/08_consulta_de_dades/01_dades_obertes/02_dades_obertes_temps_real/us_serveis_dades_API_REST.pdf). Así, una persona puede explorar los resultados visualmente y quien programa puede consultar los datos.

La ACA también advierte que, por tratarse de datos en tiempo real, las medidas no están revisadas ni validadas y pueden contener errores. Comunicar esta limitación ayuda a que el usuario valore los datos con el cuidado adecuado. La [guía de usuario y documentación de la API de Smart Region de la Diputación de Barcelona](https://smartregion.diba.cat/node/800) es otro recurso real para consultar el modelo y el uso de Sentilo.

### Mala práctica de consumo: tratar las medidas como datos validados

Un error es tratar cada valor recibido como una medida exacta y confirmada. La ACA ofrece un caso real para discutirlo: sus datos en tiempo real pueden no estar validados. Sería una mala práctica presentar esos valores como definitivos o tomar decisiones sin comprobar su fecha, unidad, contexto y controles de calidad. La ACA, en cambio, hace una buena práctica al comunicar esta limitación.

También conviene evitar estas situaciones:

- mostrar un valor sin unidad, fecha y hora;
- asumir que el punto geográfico identifica con precisión la ubicación real o el área representada;
- confundir que un servicio responda correctamente con que la medida sea correcta;
- convertir a GeoJSON sin verificar el orden de coordenadas, el sistema de referencia y el significado de los atributos.

Estas cautelas no hacen que el servicio de la ACA sea un mal ejemplo: su aviso sobre validación es una buena práctica. El caso permite distinguir la calidad de la publicación de la responsabilidad de quien interpreta y representa las observaciones.

!!! question "Pausa para comprobar · 5 minutos"

    Abrid la [API SensorThings de Hamburgo](https://iot.hamburg.de/v1.1/) y seguid los enlaces a `Things`, `Datastreams` y `Observations`. ¿Qué representa cada recurso? Después, imaginad que una observación contiene `result: 18`, una ubicación y una marca de tiempo: ¿qué información buscaríais antes de interpretarla o mostrarla en un mapa (unidad, propiedad observada, sistema de referencia, fecha de actualización u otra)?

## Para ampliar

- [SOS: estándar Sensor Observation Service del OGC (inglés)](https://www.ogc.org/standards/sos/)
- [Introducción al servicio SOS (presentación en español, IDEE)](https://www.idee.es/resources/presentaciones/JIIDE16/2016/30_art_Tracasa_GestionInteligenteRecursosHidraulicos.pdf)
- [SensorThings API: página del OGC en español](https://www.ogc.org/es/standards/sensorthings/)
- [OGC API – Connected Systems: página del OGC en español](https://www.ogc.org/es/standards/ogc-api-connected-systems/)
- [Sentilo: web oficial](https://www.sentilo.io/)
- [Documentación de la API de Sentilo (inglés)](https://sentilo.readthedocs.io/en/latest/api_docs.html)
- [Documentación FROST: consultas y más ejemplos SensorThings (inglés)](https://fraunhoferiosb.github.io/FROST-Server/sensorthingsapi/3_GettingData.html)
- [Portal de datos abiertos en tiempo real de la ACA (catalán)](https://aca.gencat.cat/ca/laigua/consulta-de-dades/dades-obertes/dades-obertes-temps-real/)
- [Sentilo en el Centro de Transferencia de Tecnología de la Administración española](https://administracionelectronica.gob.es/ctt/sentilo)

**Siguiente:** [Consumo de sensores de la ACA con Sentilo](12_ejemplo_sentilo_aca.md).
