# Comprobaciones manuales de los ejemplos

Estas comprobaciones sirven para revisar que las aplicaciones y los datos externos usados en los ejemplos siguen disponibles y mantienen la estructura que necesita el ejercicio.

Desde la raíz del repositorio, ejecútalas manualmente con:

```bash
python3 tests/manual_checks.py
```

No se ejecutan al compilar MkDocs y no están conectadas al CI. No requieren instalar paquetes de Python, pero sí conexión a Internet. Una caída temporal del portal o un límite de peticiones puede producir un fallo transitorio; si ocurre, vuelve a intentarlo y comprueba también el enlace en el navegador.

Las comprobaciones actuales revisan las API de Socrata, Zaragoza, Bicing/CityBikes, Sentilo/ACA, FGC, los feeds GTFS estáticos de EMT València y FGC, SensorThings de Hamburgo, OpenRouteService, el geocodificador del ICGC y USGS; también revisan los controles Leaflet de OpenCage y OpenRouteService, el estilo vectorial del ICGC, la versión de MapLibre usada en el ejemplo, el enlace documental de AEMET, la sincronía entre código y lección, el CSV de accidentes de 2024 y la disponibilidad de Kepler.gl Demo. Si Node.js está instalado, comprueban la sintaxis de los ejemplos JavaScript. Para Sentilo y los visores locales de la expedición y GTFS también se prueba el servidor y sus respuestas; en el caso de la expedición se comprueban con dos clientes la entrada de participantes, el envío de posiciones y la desconexión.

Para habilitar las pruebas de integración locales, instala las dependencias de cada ejemplo una vez:

```bash
npm install --prefix docs/ejemplos/mapa-expedicion-realtime
npm install --prefix docs/ejemplos/gtfs-valencia
```

Si las dependencias no están instaladas, la prueba de integración correspondiente se omite; las demás comprobaciones manuales pueden ejecutarse igualmente.

Las pruebas de OpenCage y OpenRouteService usan una clave personal solo si se definen `OPENCAGE_API_KEY` y `ORS_API_KEY` en el entorno, respectivamente. Sin esas variables, se omiten. No guardes las claves en este repositorio. Puedes definir la clave en una terminal antes de ejecutar la prueba correspondiente y borrarla al terminar.

## Copias de los visores en la documentación

Los ejemplos web ejecutables tienen una copia en `docs/ejemplos/<nombre>/`. Cuando no requieren servidor, la carpeta contiene un `index.html` que la lección enlaza al inicio. Cuando necesitan un servidor, como Socket.IO, la carpeta contiene la aplicación local completa y una vista previa estática del resultado para la documentación. Al actualizar una lección, actualiza también los archivos de su carpeta; las comprobaciones manuales verifican los enlaces y la sincronía entre el código publicado y el código explicado.
