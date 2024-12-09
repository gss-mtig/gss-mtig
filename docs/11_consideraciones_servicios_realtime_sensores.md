# Consideraciones sobre servicios de Sensores

## Problemas frecuentes al trabajar con sensores

- Existe el estándar SOS de la OGC [^1], pero tiene poca implementación, debido a que algunos de los fabricantes de sensores utilizan formatos propios, lo que dificulta la integración de sensores de diferentes proveedores en un sólo sistema.

- Datos erróneos y falsos, ya sea por una mala lectura ó porque el sensor no está funcionando correctamente. No tenemos forma de saber si el dato es correcto.

## Ejemplo de buenas prácticas

El servicio de datos sobre embalses ofrecidos por la ACA (Agencia Catalana del Agua)http://aca.gencat.cat/ca/laigua/consulta-de-dades/dades-obertes/. Es un ejemplo de buenas prácticas porque está bien documentado y contiene ejemplos. El acceso es libre y gratuito y tiene salida en un mapa para los usuarios que no sean desarrolladores.

Ejemplo de salida http://aca-web.gencat.cat/sdim2/apirest/catalog?componentType=embassament

Si bien el formato de salida es un JSON donde tiene una propiedad *location* no es un formato geográfico que podamos utilizar directamente para poner en un mapa, para ello tendríamos que hacer una transformación hacia algún formato geográfico tipo GeoJSON.

## Ejemplo de "malas" prácticas

El servicio de la DIBA https://www.diba.cat/es/web/smartregion o https://dadesobertes.diba.cat/.

El acceso a la aplicación http://sentilo.diba.cat/sentilo-catalog-web/ no es fácil de encontrar y no hay ninguna documentación.

## Referencias

[^1]: http://www.opengeospatial.org/standards/sos
