# Instrucciones para trabajar en este repositorio

## Contexto y alcance

- Este repositorio contiene materiales en español para una asignatura de 16 horas lectivas sobre geoservicios para smart cities, impartida en el Máster de Geoinformación de la UAB.
- El curso de Infraestructuras de Datos Espaciales (IDE), también de 16 horas, se mantiene en otro repositorio. Evita duplicar allí conceptos, estándares y ejemplos; confirma con el usuario antes de trasladar contenido entre asignaturas.
- La documentación fuente está en `docs/` (Markdown) y se compila con MkDocs Material usando `mkdocs.yml`.
- El usuario revisa las adaptaciones página a página. Completa el cambio solicitado y deja la siguiente decisión al usuario; no amplíes el alcance por iniciativa propia.

## Criterios pedagógicos y editoriales

- Prioriza explicaciones breves, ejemplos reales y un enfoque práctico para estudiantes de geografía, cartografía, biología y disciplinas afines, muchos de ellos principiantes en programación.
- Cuando una explicación conceptual ocupe unos 30 minutos, añade una actividad de clase de 5–10 minutos, breve y no entregable.
- En los ejemplos, guía la construcción paso a paso: explica cada etapa clave, muestra los fragmentos necesarios y deja el código completo funcional al final.
- Conserva los ejercicios entregables, su puntuación y su posición al final de la práctica. No incluyas en los ejemplos ni en el código la solución de una tarea evaluable.
- Los ejercicios para casa son opcionales salvo que el material existente los defina como entregables puntuables.
- Corrige ortografía, acentuación, claridad y consistencia terminológica. Enlaces a documentación externa en español tienen preferencia cuando ese contenido exista.
- Mantén un estilo uniforme en las páginas de ejemplo: enlace de resultado visible al principio, explicación del objetivo, pasos, código completo y actividad o ejercicio al final.

## Ejemplos web y validación

- Para cada visor práctico, mantén una copia ejecutable en `docs/ejemplos/<nombre>/` y enlázala desde su lección. En GitHub Pages, donde no se ejecutan servidores, ofrece una vista previa estática si la aplicación requiere backend.
- Mantén sincronizados los archivos del ejemplo y los bloques de código completos de la lección. Evita dependencias remotas sin versión fijada y paquetes obsoletos cuando exista una alternativa sencilla.
- Verifica las API, feeds, bibliotecas y URL externas antes de basar una actividad en ellas. Distingue la frecuencia de consulta de la frecuencia real de actualización de la fuente.
- Cada ejemplo práctico con servicios externos debe tener comprobaciones manuales de disponibilidad y estructura en `tests/manual_checks.py`; añade comprobaciones de sintaxis o integración local cuando correspondan.
- Las pruebas son solo para desarrollo: se ejecutan manualmente, no durante `mkdocs build` y no se integran en CI. Documenta dependencias necesarias para ejecutarlas.
- Tras editar MkDocs, valida con `mkdocs/bin/mkdocs build --strict` si el entorno del repositorio está disponible; comprueba también que los enlaces internos y los archivos de navegación existen.

## MkDocs, credenciales y publicación

- Actualiza `mkdocs.yml` cuando cambien páginas o navegación. Los títulos con dos puntos deben ir entre comillas; usa `use_directory_urls: true` para las URL con barra final.
- En `docs/index.md`, usa enlaces relativos a los archivos Markdown (`pagina.md`) para que funcionen en `mkdocs serve` y en GitHub Pages.
- Excluye `node_modules/` y otros archivos de desarrollo de la salida de MkDocs; no publiques dependencias instaladas ni artefactos de build como si fueran documentación.
- No guardes API keys, tokens, contraseñas ni credenciales en el código, HTML, Markdown, tests o historial nuevo. Usa variables de entorno o entradas locales cuando el ejercicio necesite una clave; nunca muestres su valor en logs o informes.
- Antes de publicar o preparar una subida, busca credenciales tanto en los archivos actuales como en el historial de Git y en la rama `gh-pages`. Si encuentras una, informa de la ruta y el commit sin revelar el valor; trata la clave como expuesta.
- No reescribas ni fuerces el historial remoto para purgar secretos sin autorización explícita. No publiques, hagas push ni despliegues sin que el usuario lo solicite.
