# 2.2. CKAN: comparación opcional

Esta página amplía el ejemplo de Socrata con una consulta breve a un portal CKAN. El propósito no es aprender dos APIs en profundidad, sino reconocer que distintos portales ofrecen mecanismos para buscar conjuntos de datos y recursos.

## Una búsqueda con la Action API

CKAN dispone de una API denominada **Action API**. Sus acciones permiten, entre otras cosas, buscar conjuntos de datos y recursos, consultar sus metadatos y acceder a las direcciones de descarga.

Por ejemplo, esta petición busca conjuntos que contengan el término `wifi` en el portal de demostración de CKAN:

```text
https://demo.ckan.org/api/3/action/package_search?q=wifi&rows=5
```

La respuesta se devuelve en JSON. En ella, `success` indica si la operación se realizó correctamente y `result` contiene los resultados. Cada conjunto puede incluir metadatos y uno o varios **recursos**, como archivos CSV o enlaces a servicios.

La búsqueda de recursos es otra acción. Su sintaxis y disponibilidad pueden depender de la versión y configuración del portal:

```text
https://demo.ckan.org/api/3/action/resource_search?query=name:wifi&limit=5
```

Antes de reutilizar estas direcciones en un proyecto, consulta la documentación del portal concreto. No todos los portales CKAN tienen los mismos datos, extensiones o configuración.

## Comparación con Socrata

| Aspecto | Socrata | CKAN |
|---|---|---|
| API habitual | SODA para consultar los registros de un conjunto | Action API para operar sobre conjuntos, recursos y otros objetos |
| Identificación | Identificador corto del conjunto, por ejemplo `erm2-nwe9` | Portal más nombre o identificador del conjunto y de sus recursos |
| Consulta típica | Filtrar, ordenar y seleccionar filas y campos con SoQL | Buscar conjuntos o recursos con una acción de la API |
| Variación entre portales | Cambian el dominio y los conjuntos publicados | Puede variar la versión, configuración y disponibilidad de acciones |

En ambos casos, la API permite automatizar el acceso a datos publicados en el portal. Sin embargo, encontrar un conjunto no equivale necesariamente a obtener sus registros: a veces hay que seguir el enlace a un recurso o consultar la API específica que ofrece ese conjunto.

!!! question "Prueba opcional"
    Abre la petición `package_search` en el navegador. Localiza el nombre de un conjunto y comprueba si incluye recursos descargables. ¿Qué diferencias observas entre esta respuesta y la lista de registros obtenida en el ejemplo de Socrata?

## Referencias

- [Documentación de la Action API de CKAN (inglés)](https://docs.ckan.org/en/latest/api/index.html)
- [Acción `package_search` (inglés)](https://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.get.package_search)
- [Acción `resource_search` (inglés)](https://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.get.resource_search)
