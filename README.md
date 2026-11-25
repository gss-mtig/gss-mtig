# GSS-mtig

[https://gss-mtig.github.io/gss-mtig/](https://gss-mtig.github.io/gss-mtig/)

## Temario

* Introducción a las Smart Cities
    * Conceptos Smart Cities
    * Conceptos Open Data
    * Conceptos sensores
    * Tecnologías OpenData

* API servicios Open data (CKAN y SOCRATA)
* Conceptos VectorTiles
* Visualización con Kepler.gl
* Herramientas de visualización de datos
* Conceptos básicos de Geoservicios
* Servicios realtime Open data
* Ejemplo servicio bicing Barcelona
* Servicios realtime sensores
* Ejemplo Sentilo ACA
* Geoservicios realtime
* Herramientas de visualización geoservicios
* Ejemplo de Geocodificador
* Ejemplo Isócronas
* Ejemplo de geoservicio realtime para compartir ubicación
* Ejemplo GTFS (Google Transit)

## Entorno de documentación

El sitio se genera con [Zensical](https://zensical.org/), usando `zensical.toml` como configuración y `docs/` como carpeta de contenidos.

Para crear el entorno e instalar las dependencias fijadas en `pyproject.toml`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

### Previsualizar y compilar

- `zensical serve`: inicia el servidor local con recarga automática.
- `zensical build`: genera el sitio estático en `site/`.

### Publicación en GitHub Pages

GitHub Actions compila y publica el sitio automáticamente al subir cambios a `main` o `master` que afecten a la documentación o su configuración. También se puede iniciar manualmente desde la pestaña **Actions**, con el workflow **Publicar documentación**. El sitio se despliega desde un artefacto de compilación; no hace falta actualizar la rama `gh-pages`.

Como configuración inicial, selecciona **Settings → Pages → Build and deployment → Source → GitHub Actions** en GitHub. Después, cada cambio subido a la rama principal iniciará el despliegue automáticamente ([instrucciones oficiales](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)).
