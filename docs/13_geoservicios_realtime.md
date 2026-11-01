# Geoservicios para localización y movilidad

Los servicios geográficos permiten resolver preguntas distintas a partir de una ubicación. Algunos responden a una consulta puntual —por ejemplo, encontrar una dirección o calcular una ruta— y otros publican posiciones o medidas que cambian con el tiempo. Saber qué pregunta queremos contestar ayuda a elegir el servicio adecuado.

| Pregunta | Tipo de servicio | Qué suele devolver | Ejemplo del curso |
|---|---|---|---|
| ¿Dónde está esta dirección o lugar? | Geocodificación | Una o varias ubicaciones candidatas con coordenadas y contexto | [Buscar direcciones y topónimos](15_ejemplo_geocodificador.md) |
| ¿Qué dirección o lugar hay cerca de estas coordenadas? | Geocodificación inversa | Una dirección o topónimo aproximado | [Geocodificador: consulta inversa](15_ejemplo_geocodificador.md#entender-la-peticion-y-la-respuesta) |
| ¿Cómo llego de un punto a otro? | Cálculo de rutas | Una ruta y, según el servicio, distancia, duración o instrucciones | Servicio de rutas de [OpenRouteService](https://openrouteservice.org/) |
| ¿A qué lugares puedo llegar en cierto tiempo? | Cálculo de isócronas | Un área alcanzable desde un punto según el modo de transporte y el tiempo | [Ejemplo de isócronas](16_ejemplo_mobility.md) |
| ¿Dónde están ahora los vehículos? | Servicio de posiciones en tiempo real | Posiciones con marca de tiempo, normalmente actualizadas de forma periódica | [Trenes de FGC en tiempo real](19_ejemplo_fgc_realtime.md) |
| ¿Qué vehículos o servicios están disponibles? | API de movilidad compartida | Estaciones o vehículos y su estado más reciente | [Bicing con MapLibre](10_ejemplo_servicio_bicing_bcn_vt.md) |

Los nombres de los servicios no garantizan que todas las respuestas tengan el mismo formato o nivel de detalle. Antes de integrarlos, revisa qué campos devuelven, la cobertura, la fecha de actualización, las condiciones de acceso y si hace falta una clave. Para un análisis puntual puede bastar una consulta; una aplicación de movilidad normalmente combina varias respuestas y debe gestionar fallos o datos desactualizados.

## Datos estáticos y datos que cambian

Un servicio en tiempo real entrega datos actualizados con cierta frecuencia, pero eso no significa necesariamente que transmita cada cambio al instante. Puede publicar posiciones cada cierto intervalo, retrasarse o no incluir todos los vehículos. Conviene comprobar la marca temporal y la frecuencia de actualización antes de describirlo como «tiempo real».

El ejemplo de FGC permite observar posiciones de trenes que se refrescan periódicamente. El de Bicing muestra otra situación: información de estaciones y disponibilidad que cambia, aunque no represente una trayectoria continua. En ambos casos, el mapa es solo una parte del sistema; la utilidad depende también de la calidad y actualización del servicio.

!!! question "Prueba breve en clase · 5–10 minutos"

    En parejas, elegid qué tipo de servicio consultaríais para cada pregunta: **encontrar la entrada de un hospital a partir de su dirección**, **estimar qué barrios quedan a 15 minutos a pie de una parada**, **ver dónde circula ahora un tren** y **comprobar si una estación de Bicing tiene bicicletas disponibles**. Para una de las preguntas, indicad qué fecha, unidad o dato de contexto comprobaríais antes de confiar en el resultado.

## Para ampliar

- [OpenRouteService: servicios de rutas, isócronas y geocodificación (inglés)](https://openrouteservice.org/)
- [Datos abiertos de FGC: posicionamiento de trenes](https://dadesobertes.fgc.cat/explore/dataset/posicionament-dels-trens/api/)
- [Bicing Barcelona: ejemplo con datos de estaciones](10_ejemplo_servicio_bicing_bcn_vt.md)
