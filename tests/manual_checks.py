"""Comprobaciones manuales de los ejemplos que dependen de servicios externos.

Ejecutar desde la raíz del repositorio con: python3 tests/manual_checks.py
"""

import csv
import io
import json
import os
import re
import shutil
import socket
import subprocess
import time
import unittest
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOCRATA_ENDPOINT = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
BARCELONA_CSV = (
    "https://opendata-ajuntament.barcelona.cat/data/dataset/"
    "e769eb9d-d778-4cd7-9e3a-5858bba49b20/resource/"
    "66f5e7e3-045b-4d19-b649-2eaea622ae93/download"
)
KEPLER_DEMO = "https://kepler.gl/demo"
USGS_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
AEMET_INFO = "https://opendata.aemet.es/centrodedescargas/info"
ZARAGOZA_PMR_API = (
    "https://www.zaragoza.es/sede/servicio/urbanismo-infraestructuras/"
    "equipamiento/aparcamiento-personas-discapacidad.geojson"
    "?srsname=wgs84&start=0&rows=50"
)
BICING_GBFS_BASE = "https://api.citybik.es/gbfs/2/bicing"
BICING_MAP_STYLE = "https://geoserveis.icgc.cat/contextmaps/icgc.json"
MAPLIBRE_JS = "https://unpkg.com/maplibre-gl@5.12.0/dist/maplibre-gl.js"
SENSORTHINGS_HAMBURG = "https://iot.hamburg.de/v1.1/"
ACA_SENTILO_CATALOG = (
    "https://aplicacions.aca.gencat.cat/sdim2/apirest/catalog"
    "?componentType=embassament"
)
ACA_SENTILO_DATA = "https://aplicacions.aca.gencat.cat/sdim2/apirest/data"
ACA_SENTILO_PROVIDER = "EMBASSAMENT-EST"
SENTILO_EXAMPLE_DIR = ROOT / "docs/ejemplos/sentilo-aca"
OPENCAGE_API = "https://api.opencagedata.com/geocode/v1/json"
OPENCAGE_LEAFLET_PLUGIN_VERSION = "v2.1.0"
OPENCAGE_LEAFLET_PLUGIN_JS = (
    "https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@"
    f"{OPENCAGE_LEAFLET_PLUGIN_VERSION}/dist/js/L.Control.OpenCageGeocoding.min.js"
)
OPENCAGE_LEAFLET_PLUGIN_CSS = (
    "https://cdn.jsdelivr.net/gh/opencagedata/leaflet-opencage-geocoding@"
    f"{OPENCAGE_LEAFLET_PLUGIN_VERSION}/dist/css/L.Control.OpenCageGeocoding.min.css"
)
OPENCAGE_EXAMPLE_DIR = ROOT / "docs/ejemplos/geocodificador-opencage"
ICGC_GEOCODER_BASE = "https://eines.icgc.cat/geocodificador"
ICGC_EXAMPLE_DIR = ROOT / "docs/ejemplos/geocodificador-icgc"
ORS_ISOCHRONES_API = "https://api.heigit.org/openrouteservice/v2/isochrones"
ORS_EXAMPLE_DIR = ROOT / "docs/ejemplos/mobility-isochrones"
ORS_REACHABILITY_VERSION = "v2.0.2"
ORS_REACHABILITY_JS = (
    "https://cdn.jsdelivr.net/gh/trafforddatalab/leaflet.reachability@"
    f"{ORS_REACHABILITY_VERSION}/leaflet.reachability.js"
)
ORS_REACHABILITY_CSS = (
    "https://cdn.jsdelivr.net/gh/trafforddatalab/leaflet.reachability@"
    f"{ORS_REACHABILITY_VERSION}/leaflet.reachability.css"
)
REALTIME_EXAMPLE_DIR = ROOT / "docs/ejemplos/mapa-expedicion-realtime"
FGC_TRAINS_API = (
    "https://dadesobertes.fgc.cat/api/explore/v2.1/catalog/datasets/"
    "posicionament-dels-trens/exports/geojson?lang=es&timezone=Europe%2FMadrid"
)
FGC_LINES_API = (
    "https://dadesobertes.fgc.cat/api/explore/v2.1/catalog/datasets/"
    "lineas-red-fgc/exports/json?lang=es&timezone=Europe%2FMadrid"
)
FGC_EXAMPLE_DIR = ROOT / "docs/ejemplos/fgc-trenes-realtime"
VALENCIA_GTFS_URL = (
    "https://opendata.vlci.valencia.es/dataset/ab058cf8-ad3e-4d9c-ac89-"
    "0c6367ecf351/resource/c81b69e6-c082-44dc-acc6-66fc417b4e66/download/google_transit.zip"
)
FGC_GTFS_URL = "https://www.fgc.cat/google/google_transit.zip"
GTFS_EXAMPLE_DIR = ROOT / "docs/ejemplos/gtfs-valencia"


def fetch(url, max_bytes=None, headers=None):
    request_headers = {"User-Agent": "gss-mtig-manual-check/1.0"}
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    with urlopen(request, timeout=30) as response:
        body = response.read(max_bytes) if max_bytes else response.read()
        return response.status, response.headers, body


def fetch_opencage(url):
    try:
        return fetch(url)
    except HTTPError as error:
        with error:
            return error.code, error.headers, error.read()
    except URLError as error:
        raise AssertionError(f"OpenCage request failed: {error.reason}") from None


def html_example_from_lesson(lesson, section_heading=None):
    if section_heading:
        lesson = lesson.split(section_heading, 1)[1]
    match = re.search(r"```html\s*\n(.*?)\n```", lesson, re.DOTALL)
    if not match:
        raise AssertionError("No se encontró un bloque HTML completo en la lección")
    return match.group(1) + "\n"


def code_block_after_heading(lesson, heading):
    section = lesson.split(heading, 1)[1]
    match = re.search(r"```(?:html|js|json|css)\s*\n(.*?)\n```", section, re.DOTALL)
    if not match:
        raise AssertionError(f"No se encontró un bloque de código después de {heading!r}")
    return match.group(1) + "\n"


class ManualExerciseChecks(unittest.TestCase):
    def test_socrata_api_returns_311_records_with_expected_fields(self):
        query = urlencode(
            {
                "$select": "unique_key,created_date,complaint_type,borough,latitude,longitude",
                "$where": "borough = 'MANHATTAN'",
                "$limit": "1",
            }
        )
        status, headers, body = fetch(f"{SOCRATA_ENDPOINT}?{query}")
        records = json.loads(body.decode("utf-8"))

        self.assertEqual(status, 200)
        self.assertIn("json", headers.get("Content-Type", "").lower())
        self.assertIsInstance(records, list)
        self.assertTrue(records, "La consulta no devolvió registros")
        self.assertTrue(
            {"unique_key", "created_date", "complaint_type", "borough", "latitude", "longitude"}
            <= records[0].keys()
        )

    def test_socrata_visual_example_and_lesson_use_the_api(self):
        page = (ROOT / "docs/ejemplos/socrata-311/index.html").read_text(encoding="utf-8")
        lesson = (ROOT / "docs/2_1_api_socrata.md").read_text(encoding="utf-8")

        self.assertIn(SOCRATA_ENDPOINT, page)
        self.assertIn("fetch(url)", page)
        self.assertIn('id="resultados"', page)
        self.assertIn(SOCRATA_ENDPOINT, lesson)

    def test_barcelona_accidents_csv_has_wgs84_coordinates(self):
        status, headers, body = fetch(BARCELONA_CSV, max_bytes=2_000_000)
        self.assertEqual(status, 200)

        text = body.decode("utf-8-sig", errors="replace")
        header = text.splitlines()[0]
        delimiter = max(",;\t", key=header.count)
        self.assertGreater(header.count(delimiter), 0, "No se encontró el encabezado del CSV")

        rows = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        self.assertIsNotNone(rows.fieldnames)
        fields = {field.strip().casefold() for field in rows.fieldnames or []}
        self.assertIn("latitud_wgs84", fields)
        self.assertIn("longitud_wgs84", fields)

        lat_field = next(field for field in rows.fieldnames if field.strip().casefold() == "latitud_wgs84")
        lon_field = next(field for field in rows.fieldnames if field.strip().casefold() == "longitud_wgs84")
        for row in rows:
            try:
                latitude = float(row[lat_field].replace(",", "."))
                longitude = float(row[lon_field].replace(",", "."))
            except (AttributeError, ValueError):
                continue
            self.assertTrue(40 <= latitude <= 42, f"Latitud inesperada: {latitude}")
            self.assertTrue(1 <= longitude <= 3, f"Longitud inesperada: {longitude}")
            break
        else:
            self.fail("No se encontraron coordenadas WGS84 numéricas en el CSV")

    def test_kepler_demo_is_reachable(self):
        status, headers, body = fetch(KEPLER_DEMO, max_bytes=500_000)
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("Content-Type", "").lower())
        self.assertIn(b"kepler", body.lower())

    def test_kepler_lesson_uses_current_demo_and_dataset(self):
        lesson = (ROOT / "docs/4_visualizacion_kepler.md").read_text(encoding="utf-8")

        self.assertIn(KEPLER_DEMO, lesson)
        self.assertIn(BARCELONA_CSV, lesson)
        self.assertIn("Latitud_WGS84", lesson)
        self.assertIn("Longitud_WGS84", lesson)

    def test_usgs_geojson_feed_has_expected_structure(self):
        status, headers, body = fetch(USGS_FEED)
        feed = json.loads(body.decode("utf-8"))

        self.assertEqual(status, 200)
        self.assertIn("json", headers.get("Content-Type", "").lower())
        self.assertEqual(feed.get("type"), "FeatureCollection")
        self.assertIn("metadata", feed)
        self.assertIsInstance(feed.get("features"), list)
        if feed["features"]:
            self.assertEqual(feed["features"][0].get("geometry", {}).get("type"), "Point")

    def test_aemet_documentation_link_is_in_lesson(self):
        lesson = (ROOT / "docs/2_3_consideraciones_open_data.md").read_text(encoding="utf-8")

        self.assertIn(AEMET_INFO, lesson)
        self.assertIn(USGS_FEED.rsplit("/summary/", 1)[0] + "/geojson.php", lesson)

    def test_hamburg_sensorthings_api_exposes_core_resources(self):
        status, headers, body = fetch(SENSORTHINGS_HAMBURG)
        service = json.loads(body.decode("utf-8"))
        lesson = (ROOT / "docs/11_consideraciones_servicios_realtime_sensores.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(status, 200)
        self.assertIn("json", headers.get("Content-Type", "").lower())
        resources = {resource.get("name") for resource in service.get("value", [])}
        self.assertTrue({"Things", "Datastreams", "Observations"} <= resources)
        self.assertIn(SENSORTHINGS_HAMBURG, lesson)

    def test_aca_sentilo_catalog_contains_georeferenced_embassaments(self):
        status, headers, body = fetch(ACA_SENTILO_CATALOG)
        catalog = json.loads(body.decode("utf-8"))
        providers = catalog.get("providers", [])
        provider = next(
            (item for item in providers if item.get("provider") == ACA_SENTILO_PROVIDER),
            None,
        )

        self.assertEqual(status, 200)
        self.assertIn("json", headers.get("Content-Type", "").lower())
        self.assertIsNotNone(provider, "No se encontró el proveedor de embalses de la ACA")
        self.assertTrue(provider.get("sensors"), "El catálogo no devolvió sensores")

        for sensor in provider["sensors"]:
            location = str(sensor.get("location") or "").split()
            if len(location) != 2:
                continue
            try:
                latitude, longitude = map(float, location)
            except ValueError:
                continue
            self.assertIn("sensor", sensor)
            self.assertIn("component", sensor)
            self.assertTrue(40 <= latitude <= 43, f"Latitud inesperada: {latitude}")
            self.assertTrue(0 <= longitude <= 4, f"Longitud inesperada: {longitude}")
            break
        else:
            self.fail("No se encontró ningún sensor de embalse con coordenadas válidas")

    def test_aca_sentilo_latest_observation_uses_sensor_identifier(self):
        _, _, catalog_body = fetch(ACA_SENTILO_CATALOG)
        catalog = json.loads(catalog_body.decode("utf-8"))
        provider = next(
            item for item in catalog.get("providers", [])
            if item.get("provider") == ACA_SENTILO_PROVIDER
        )
        sensor = next(
            item for item in provider.get("sensors", []) if item.get("sensor")
        )
        url = (
            f"{ACA_SENTILO_DATA}/{ACA_SENTILO_PROVIDER}/"
            f"{sensor['sensor']}"
        )
        status, headers, body = fetch(url)
        data = json.loads(body.decode("utf-8"))

        self.assertEqual(status, 200)
        self.assertIn("json", headers.get("Content-Type", "").lower())
        self.assertIsInstance(data.get("observations"), list)
        if data["observations"]:
            self.assertTrue({"value", "timestamp"} <= data["observations"][0].keys())

    def test_sentilo_app_files_match_lesson_and_javascript_is_valid(self):
        lesson_path = ROOT / "docs/12_ejemplo_sentilo_aca.md"
        lesson = lesson_path.read_text(encoding="utf-8")
        self.assertIn("(ejemplos/sentilo-aca/index.html)", lesson)

        for filename in ("server.js", "aca-data.js", "index.html", "aca-map.js"):
            with self.subTest(file=filename):
                heading = f"### Código de `{filename}`"
                self.assertEqual(
                    (SENTILO_EXAMPLE_DIR / filename).read_text(encoding="utf-8"),
                    code_block_after_heading(lesson, heading),
                )

        self.assertTrue((SENTILO_EXAMPLE_DIR / "preview.png").is_file())
        server = (SENTILO_EXAMPLE_DIR / "server.js").read_text(encoding="utf-8")
        browser_code = (SENTILO_EXAMPLE_DIR / "aca-map.js").read_text(encoding="utf-8")
        self.assertIn("/catalog?componentType=embassament", server)
        self.assertIn("/data/:provider/:sensor", server)
        self.assertIn("/api/catalog", browser_code)
        self.assertIn("/api/data/", browser_code)
        self.assertNotIn("lastOb", server + browser_code)
        self.assertNotIn("providers[1]", server + browser_code)

        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js no está instalado; se omite la comprobación de sintaxis JS")

        for filename in ("server.js", "aca-data.js", "aca-map.js"):
            with self.subTest(syntax=filename):
                result = subprocess.run(
                    [node, "--check", str(SENTILO_EXAMPLE_DIR / filename)],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

        sample = {
            "providers": [{
                "provider": ACA_SENTILO_PROVIDER,
                "sensors": [
                    {
                        "sensor": "080581-002-ANA006",
                        "component": "080581-002",
                        "componentDesc": "Foix (Castellet i la Gornal)",
                        "description": "Nivell absolut",
                        "location": "41.255617318 1.651034658",
                        "unit": "msnm",
                    },
                    {
                        "sensor": "080581-002-ANA007",
                        "component": "080581-002",
                        "componentDesc": "Foix (Castellet i la Gornal)",
                        "description": "Volum embassat",
                        "location": "41.255617318 1.651034658",
                        "unit": "hm3",
                    },
                    {
                        "sensor": "sin-coordenadas",
                        "component": "080581-003",
                        "location": "",
                    },
                ],
            }],
        }
        module_path = json.dumps(str(SENTILO_EXAMPLE_DIR / "aca-data.js"))
        script = (
            f"const {{ catalogToGeoJSON }} = require({module_path}); "
            "const input = JSON.parse(require('fs').readFileSync(0, 'utf8')); "
            "process.stdout.write(JSON.stringify(catalogToGeoJSON(input)));"
        )
        result = subprocess.run(
            [node, "-e", script],
            input=json.dumps(sample),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        geojson = json.loads(result.stdout)
        self.assertEqual(geojson.get("type"), "FeatureCollection")
        self.assertEqual(len(geojson["features"]), 1)
        feature = geojson["features"][0]
        self.assertEqual(feature["geometry"]["coordinates"], [1.651034658, 41.255617318])
        self.assertEqual(
            [sensor["id"] for sensor in feature["properties"]["sensors"]],
            ["080581-002-ANA006", "080581-002-ANA007"],
        )

    def test_zaragoza_pmr_api_returns_georeferenced_features(self):
        status, headers, body = fetch(ZARAGOZA_PMR_API)
        data = json.loads(body.decode("utf-8"))
        lesson = (ROOT / "docs/8_ejemplo_parking_movilidad_reducida_zaragoza.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(status, 200)
        self.assertIn("json", headers.get("Content-Type", "").lower())
        self.assertTrue(
            headers.get("Access-Control-Allow-Origin"),
            "La respuesta no anuncia acceso CORS para usar fetch desde una página local",
        )
        self.assertEqual(data.get("type"), "FeatureCollection")
        self.assertTrue(data.get("features"), "La API no devolvió aparcamientos PMR")
        feature = data["features"][0]
        self.assertEqual(feature.get("geometry", {}).get("type"), "Point")
        self.assertGreaterEqual(len(feature["geometry"].get("coordinates", [])), 2)
        self.assertIn(ZARAGOZA_PMR_API, lesson)
        self.assertIn("features.forEach", lesson)
        self.assertIn("Práctica opcional en casa", lesson)

    def test_zaragoza_pmr_demo_is_linked_and_matches_the_lesson(self):
        lesson_path = ROOT / "docs/8_ejemplo_parking_movilidad_reducida_zaragoza.md"
        demo_path = ROOT / "docs/ejemplos/zaragoza-pmr/index.html"
        lesson = lesson_path.read_text(encoding="utf-8")

        self.assertIn("(ejemplos/zaragoza-pmr/index.html)", lesson)
        self.assertEqual(
            demo_path.read_text(encoding="utf-8"),
            html_example_from_lesson(lesson, "## 5. Código completo"),
        )

    def test_bicing_gbfs_station_feeds_are_available(self):
        payloads = {}
        for feed_name in ("station_information", "station_status"):
            with self.subTest(feed=feed_name):
                status, headers, body = fetch(f"{BICING_GBFS_BASE}/{feed_name}.json")
                payload = json.loads(body.decode("utf-8"))
                self.assertEqual(status, 200)
                self.assertIn("json", headers.get("Content-Type", "").lower())
                self.assertTrue(headers.get("Access-Control-Allow-Origin"))
                self.assertIn("data", payload)
                self.assertIn("stations", payload["data"])
                self.assertTrue(payload["data"]["stations"])
                payloads[feed_name] = payload

        info = payloads["station_information"]["data"]["stations"][0]
        status = payloads["station_status"]["data"]["stations"][0]
        self.assertTrue({"station_id", "lat", "lon", "name"} <= info.keys())
        self.assertNotIn("capacity", info)
        self.assertTrue(
            {"station_id", "num_bikes_available", "num_docks_available"} <= status.keys()
        )

    def test_bicing_maplibre_lesson_uses_current_feeds_and_vector_style(self):
        lesson = (ROOT / "docs/10_ejemplo_servicio_bicing_bcn_vt.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(BICING_GBFS_BASE + "/station_information.json", lesson)
        self.assertIn(BICING_GBFS_BASE + "/station_status.json", lesson)
        self.assertIn(BICING_MAP_STYLE, lesson)
        self.assertIn("maplibregl.Map", lesson)
        self.assertIn("capacity: bikes + docks", lesson)
        self.assertNotIn("station.capacity", lesson)
        self.assertIn("Leaflet y MapLibre permiten", lesson)
        self.assertNotIn("TOKEN OPEN DATA", lesson)
        self.assertIn("Ejercicio entregable · 2 puntos", lesson)
        self.assertIn("rangos del tamaño", lesson)
        self.assertIn("rango de colores", lesson)

    def test_bicing_maplibre_demo_is_linked_and_matches_the_lesson(self):
        lesson_path = ROOT / "docs/10_ejemplo_servicio_bicing_bcn_vt.md"
        demo_path = ROOT / "docs/ejemplos/bicing-maplibre/index.html"
        lesson = lesson_path.read_text(encoding="utf-8")

        self.assertIn("(ejemplos/bicing-maplibre/index.html)", lesson)
        for stage in (
            "### 1. Crear el mapa base con MapLibre",
            "### 2. Descargar los dos feeds",
            "### 3. Relacionar estaciones y crear GeoJSON",
            "### 4. Añadir una fuente y una capa de puntos",
            "### 5. Añadir interacción y actualizar los datos",
            "### 6. Ejecutar y probar la aplicación",
            "## Código completo",
        ):
            self.assertIn(stage, lesson)
        self.assertEqual(
            demo_path.read_text(encoding="utf-8"),
            html_example_from_lesson(lesson, "## Código completo"),
        )

    def test_icgc_maplibre_style_includes_vector_sources(self):
        status, headers, body = fetch(BICING_MAP_STYLE)
        style = json.loads(body.decode("utf-8"))

        self.assertEqual(status, 200)
        self.assertIn("json", headers.get("Content-Type", "").lower())
        self.assertTrue(
            any(source.get("type") == "vector" for source in style.get("sources", {}).values()),
            "El estilo del ICGC ya no declara fuentes vectoriales",
        )

    def test_maplibre_version_used_in_bicing_lesson_is_available(self):
        status, headers, body = fetch(MAPLIBRE_JS, max_bytes=500_000)
        lesson = (ROOT / "docs/10_ejemplo_servicio_bicing_bcn_vt.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(status, 200)
        self.assertIn("javascript", headers.get("Content-Type", "").lower())
        self.assertIn(b"maplibregl", body.lower())
        self.assertIn(MAPLIBRE_JS, lesson)

    def test_icgc_geocoder_direct_and_reverse_apis_return_geojson(self):
        direct_url = (
            f"{ICGC_GEOCODER_BASE}/cerca?"
            + urlencode({"text": "nou 10,girona", "layers": "address", "size": 1})
        )
        reverse_url = (
            f"{ICGC_GEOCODER_BASE}/invers?"
            + urlencode(
                {
                    "lat": "41.39836479",
                    "lon": "1.8566894531250002",
                    "layers": "address,topo1,topo2",
                    "size": 5,
                }
            )
        )

        for operation, url in (("direct", direct_url), ("reverse", reverse_url)):
            with self.subTest(operation=operation):
                status, headers, body = fetch(
                    url,
                    headers={"Origin": "http://localhost:8000"},
                )
                data = json.loads(body.decode("utf-8"))
                self.assertEqual(status, 200)
                self.assertIn("json", headers.get("Content-Type", "").lower())
                self.assertEqual(headers.get("Access-Control-Allow-Origin"), "*")
                self.assertEqual(data.get("type"), "FeatureCollection")
                self.assertTrue(data.get("features"), "La API no devolvió resultados")
                feature = data["features"][0]
                self.assertEqual(feature.get("geometry", {}).get("type"), "Point")
                longitude, latitude = feature["geometry"]["coordinates"][:2]
                self.assertTrue(0 <= longitude <= 4, f"Longitud inesperada: {longitude}")
                self.assertTrue(40 <= latitude <= 43, f"Latitud inesperada: {latitude}")

    def test_opencage_api_with_local_key_if_provided(self):
        api_key = os.environ.get("OPENCAGE_API_KEY")
        if not api_key:
            self.skipTest("Define OPENCAGE_API_KEY para consultar OpenCage con una clave propia")

        for query in ("Plaça de Catalunya, Barcelona", "41.387,2.17"):
            with self.subTest(query_type="coordinates" if "," in query and query[0].isdigit() else "address"):
                url = f"{OPENCAGE_API}?" + urlencode(
                    {
                        "key": api_key,
                        "q": query,
                        "countrycode": "es",
                        "language": "es",
                        "limit": 1,
                    }
                )
                status, headers, body = fetch_opencage(url)
                data = json.loads(body.decode("utf-8"))
                self.assertEqual(
                    status,
                    200,
                    f"OpenCage: {data.get('status', {}).get('message', 'respuesta no válida')}",
                )
                self.assertIn("json", headers.get("Content-Type", "").lower())
                self.assertEqual(data.get("status", {}).get("code"), 200)
                self.assertTrue(data.get("results"), "OpenCage no devolvió resultados")
                geometry = data["results"][0].get("geometry", {})
                self.assertTrue({"lat", "lng"} <= geometry.keys())

    def test_opencage_leaflet_plugin_assets_are_available(self):
        for asset, expected_content_type in (
            (OPENCAGE_LEAFLET_PLUGIN_JS, "javascript"),
            (OPENCAGE_LEAFLET_PLUGIN_CSS, "text/css"),
        ):
            with self.subTest(asset=asset.rsplit("/", 1)[-1]):
                status, headers, body = fetch(asset, max_bytes=500_000)
                self.assertEqual(status, 200)
                self.assertIn(expected_content_type, headers.get("Content-Type", "").lower())
                self.assertTrue(body)

        lesson = (ROOT / "docs/15_ejemplo_geocodificador.md").read_text(encoding="utf-8")
        page = (OPENCAGE_EXAMPLE_DIR / "index.html").read_text(encoding="utf-8")
        app_code = (OPENCAGE_EXAMPLE_DIR / "app.js").read_text(encoding="utf-8")
        self.assertIn(OPENCAGE_LEAFLET_PLUGIN_JS, page)
        self.assertIn(OPENCAGE_LEAFLET_PLUGIN_CSS, page)
        self.assertIn("L.Control.openCageGeocoding", app_code)
        self.assertIn('id="search-form"', page)
        self.assertIn('id="query"', page)
        self.assertIn('getElementById("search-form")', app_code)
        self.assertIn('requestOpenCage({ q: query, limit: "5" })', app_code)
        self.assertIn('map.on("click"', app_code)
        self.assertIn("leaflet-opencage-geocoding", lesson)
        self.assertIn("address.textContent = result.formatted", app_code)
        self.assertNotIn("confidence", app_code)
        self.assertNotIn("municipality", app_code)
        self.assertNotIn("components._category", app_code)
        self.assertNotIn("components._type", app_code)
        self.assertIn("Ejercicio entregable · 2 puntos", lesson)

    def test_geocoder_apps_match_lesson_and_have_valid_javascript(self):
        examples = (
            (
                OPENCAGE_EXAMPLE_DIR,
                ROOT / "docs/15_ejemplo_geocodificador.md",
                "OpenCage",
            ),
            (
                ICGC_EXAMPLE_DIR,
                ROOT / "docs/15_ejemplo_geocodificador_icgc.md",
                "ICGC",
            ),
        )
        node = shutil.which("node")

        for example_dir, lesson_path, title in examples:
            with self.subTest(example=title):
                lesson = lesson_path.read_text(encoding="utf-8")
                relative_path = example_dir.relative_to(ROOT / "docs/ejemplos").as_posix()
                self.assertIn(f"(ejemplos/{relative_path}/index.html)", lesson)
                for filename in ("index.html", "app.js"):
                    heading = f"### Código de `{filename}`"
                    self.assertEqual(
                        (example_dir / filename).read_text(encoding="utf-8"),
                        code_block_after_heading(lesson, heading),
                    )

                app_code = (example_dir / "app.js").read_text(encoding="utf-8")
                self.assertIn("fetch(", app_code)
                if title == "OpenCage":
                    for stage in (
                        "## Construir la aplicación paso a paso",
                        "### 1. Crear el mapa y preparar sus capas",
                        "### 2. Activar el control de búsqueda",
                        "### 3. Consultar la API con `fetch`",
                        "### 4. Consultar una dirección desde el mapa",
                    ):
                        self.assertIn(stage, lesson)
                    self.assertIn(OPENCAGE_API, app_code)
                    self.assertIn("keyInput.value", app_code)
                    self.assertIn("components.municipality", lesson)
                    self.assertNotIn("municipality", app_code)
                    self.assertNotIn("confidence", app_code)
                    self.assertNotRegex(
                        app_code + lesson,
                        r"(?i)(?:key|api[_-]?key)\s*[:=]\s*['\"][a-f0-9]{32}['\"]",
                    )
                else:
                    self.assertIn(ICGC_GEOCODER_BASE, app_code)
                    self.assertIn("${serviceUrl}/${operation}", app_code)
                    self.assertIn('"cerca"', app_code)
                    self.assertIn('"invers"', app_code)
                    self.assertIn("Ejercicio entregable · 2 puntos", lesson)
                    self.assertIn("propiedad `layer`", lesson)
                    self.assertIn('size: "1"', app_code)
                    self.assertNotIn('size: "3"', app_code)
                    self.assertNotIn("properties.layer", app_code)

                if not node:
                    continue
                result = subprocess.run(
                    [node, "--check", str(example_dir / "app.js")],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)


    def test_mobility_demo_matches_lesson_and_has_valid_javascript(self):
        lesson = (ROOT / "docs/16_ejemplo_mobility.md").read_text(encoding="utf-8")
        demo_path = ORS_EXAMPLE_DIR / "index.html"
        demo = demo_path.read_text(encoding="utf-8")

        self.assertIn("(ejemplos/mobility-isochrones/index.html)", lesson)
        self.assertNotIn('!!! tip "Ver el resultado"', lesson)
        for stage in (
            "### 1. Preparar el mapa y una capa GeoJSON",
            "### 2. Añadir el control de `leaflet.reachability`",
            "### 3. Construir una petición propia con `fetch`",
            "### 4. Comprobar y dibujar la respuesta",
            "## Código completo",
        ):
            self.assertIn(stage, lesson)
        self.assertEqual(demo, html_example_from_lesson(lesson, "## Código completo"))
        self.assertIn(ORS_ISOCHRONES_API, demo)
        self.assertIn(ORS_REACHABILITY_JS, demo)
        self.assertIn(ORS_REACHABILITY_CSS, demo)
        self.assertIn("L.control.reachability", demo)
        self.assertIn('type="password"', demo)
        self.assertIn("locations: [coordinates]", demo)
        self.assertNotIn("YOUR-API-KEY", demo)
        self.assertIn("Ejercicio entregable · 2 puntos", lesson)
        self.assertIn("un perfil válido de OpenRouteService que no aparezca", lesson)
        self.assertIn("el parámetro `range`", lesson)
        self.assertIn("range: [rangeSeconds]", demo)
        self.assertNotIn("wheelchair", demo)

        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js no está instalado; se omite la comprobación de sintaxis JS")

        scripts = re.findall(r"<script>(.*?)</script>", demo, re.DOTALL)
        self.assertTrue(scripts, "No se encontró el JavaScript de la aplicación")
        result = subprocess.run(
            [node, "--check"], input=scripts[-1], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_example_result_links_use_consistent_plain_text_style(self):
        pages = (
            "docs/8_ejemplo_parking_movilidad_reducida_zaragoza.md",
            "docs/10_ejemplo_servicio_bicing_bcn_vt.md",
            "docs/12_ejemplo_sentilo_aca.md",
            "docs/15_ejemplo_geocodificador.md",
            "docs/15_ejemplo_geocodificador_icgc.md",
            "docs/16_ejemplo_mobility.md",
        )
        for relative_path in pages:
            with self.subTest(page=relative_path):
                lesson = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("**Resultado final:** [abre ", lesson)
                self.assertNotIn('!!! tip "Ver el resultado"', lesson)
                self.assertRegex(lesson, r"\*\*Resultado final:\*\* \[abre .+\]\(ejemplos/.+/index\.html\)")

    def test_leaflet_reachability_plugin_assets_use_current_api(self):
        demo = (ORS_EXAMPLE_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn(ORS_REACHABILITY_VERSION, demo)
        self.assertIn("L.control.reachability", demo)

        for asset in (ORS_REACHABILITY_JS, ORS_REACHABILITY_CSS):
            with self.subTest(asset=asset.rsplit("/", 1)[-1]):
                status, _, body = fetch(asset, max_bytes=1_000_000)
                self.assertEqual(status, 200)
                self.assertTrue(body)
                if asset.endswith(".js"):
                    self.assertIn(b"api.heigit.org/openrouteservice/v2/isochrones", body)

    def test_openrouteservice_isochrones_api_with_local_key_if_provided(self):
        api_key = os.environ.get("ORS_API_KEY")
        if not api_key:
            self.skipTest("Define ORS_API_KEY para consultar OpenRouteService con una clave propia")

        request = Request(
            f"{ORS_ISOCHRONES_API}/cycling-regular",
            data=json.dumps(
                {
                    "locations": [[2.1686, 41.3874]],
                    "range_type": "time",
                    "range": [600],
                    "location_type": "start",
                }
            ).encode("utf-8"),
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json",
                "Accept": "application/geo+json",
                "User-Agent": "gss-mtig-manual-check/1.0",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                status, headers, body = response.status, response.headers, response.read()
        except HTTPError as error:
            with error:
                status, headers, body = error.code, error.headers, error.read()

        data = json.loads(body.decode("utf-8"))
        self.assertEqual(
            status,
            200,
            f"OpenRouteService respondió HTTP {status}: "
            f"{data.get('error', {}).get('message', 'respuesta no válida')}",
        )
        self.assertIn("json", headers.get("Content-Type", "").lower())
        self.assertEqual(data.get("type"), "FeatureCollection")
        self.assertTrue(data.get("features"), "OpenRouteService no devolvió isócronas")
        self.assertEqual(data["features"][0].get("geometry", {}).get("type"), "Polygon")

    def test_valencia_and_fgc_gtfs_zip_feeds_are_current_and_readable(self):
        for city, url in (("València EMT", VALENCIA_GTFS_URL), ("FGC", FGC_GTFS_URL)):
            with self.subTest(feed=city):
                status, headers, body = fetch(url)
                self.assertEqual(status, 200)
                self.assertTrue(
                    "zip" in headers.get("Content-Type", "").lower()
                    or body.startswith(b"PK"),
                    "El recurso no parece un archivo ZIP",
                )
                with zipfile.ZipFile(io.BytesIO(body)) as feed:
                    names = {item.rsplit("/", 1)[-1] for item in feed.namelist()}
                    self.assertTrue({"stops.txt", "shapes.txt"} <= names)
                    for filename, fields in (
                        ("stops.txt", {"stop_id", "stop_name", "stop_lat", "stop_lon"}),
                        ("shapes.txt", {"shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"}),
                    ):
                        member = next(item for item in feed.namelist() if item.rsplit("/", 1)[-1] == filename)
                        content = feed.read(member).decode("utf-8-sig")
                        rows = csv.DictReader(io.StringIO(content))
                        self.assertTrue(fields <= set(rows.fieldnames or []), f"{city}: cabeceras inesperadas en {filename}")
                        first_row = next(rows, None)
                        self.assertIsNotNone(first_row, f"{city}: {filename} está vacío")
                        if filename == "stops.txt":
                            self.assertTrue(-180 <= float(first_row["stop_lon"]) <= 180)
                            self.assertTrue(-90 <= float(first_row["stop_lat"]) <= 90)

    def test_gtfs_application_matches_lesson_and_static_preview(self):
        lesson = (ROOT / "docs/18_ejemplo_gtfs.md").read_text(encoding="utf-8")
        self.assertIn("(ejemplos/gtfs-valencia/index.html)", lesson)
        for filename, heading in (
            ("package.json", "### `package.json`"),
            ("server.js", "### `server.js`"),
            ("public/index.html", "### `public/index.html`"),
            ("public/app.js", "### `public/app.js`"),
            ("public/style.css", "### `public/style.css`"),
        ):
            with self.subTest(file=filename):
                self.assertEqual(
                    (GTFS_EXAMPLE_DIR / filename).read_text(encoding="utf-8"),
                    code_block_after_heading(lesson, heading),
                )

        self.assertIn("## Ejercicio entregable (2,5 puntos)", lesson)
        for assignment in (
            "Carga en el visor el feed GTFS estático de",
            "Añade un popup a las líneas que muestre el valor de `shape_id`",
            "Añade al mapa los trenes en tiempo real de FGC",
        ):
            self.assertIn(assignment, lesson)

        preview = (GTFS_EXAMPLE_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn('lineas: "data/shapes.geojson"', preview)
        self.assertIn('paradas: "data/stops.geojson"', preview)
        for filename in ("stops.geojson", "shapes.geojson"):
            with self.subTest(preview_data=filename):
                data = json.loads((GTFS_EXAMPLE_DIR / "data" / filename).read_text(encoding="utf-8"))
                self.assertEqual(data.get("type"), "FeatureCollection")
                self.assertTrue(data.get("features"))
        app_code = (GTFS_EXAMPLE_DIR / "public/app.js").read_text(encoding="utf-8")
        self.assertNotIn("bindPopup(feature.properties.shape_id)", app_code)
        self.assertIn("Datos EMT València", app_code)
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js no está instalado; se omite la comprobación de sintaxis JS")
        for filename in ("server.js", "public/app.js"):
            result = subprocess.run(
                [node, "--check", str(GTFS_EXAMPLE_DIR / filename)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_gtfs_local_server_serves_converted_geojson(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js no está instalado; se omite la integración del servidor GTFS")
        dependencies = subprocess.run(
            [node, "-e", "require.resolve('express'); require.resolve('jszip'); require.resolve('csv-parse/sync')"],
            cwd=GTFS_EXAMPLE_DIR,
            capture_output=True,
            text=True,
        )
        if dependencies.returncode:
            self.skipTest("Instala las dependencias del ejemplo con npm install para probar el servidor")

        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        environment = os.environ.copy()
        environment.update({"PORT": str(port), "GTFS_URL": VALENCIA_GTFS_URL})
        server = subprocess.Popen(
            [node, str(GTFS_EXAMPLE_DIR / "server.js")],
            cwd=GTFS_EXAMPLE_DIR,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                if server.poll() is not None:
                    output = server.communicate()[0]
                    self.fail(f"El servidor GTFS terminó al iniciar:\n{output}")
                try:
                    status, headers, body = fetch(f"http://127.0.0.1:{port}/")
                    break
                except URLError:
                    time.sleep(0.2)
            else:
                self.fail("El servidor GTFS no respondió en 45 segundos")

            self.assertEqual(status, 200)
            self.assertIn("text/html", headers.get("Content-Type", "").lower())
            self.assertIn(b"EMT Val\xc3\xa8ncia", body)
            for endpoint, geometry, minimum in (("stops", "Point", 100), ("shapes", "LineString", 10)):
                with self.subTest(endpoint=endpoint):
                    status, _, response = fetch(f"http://127.0.0.1:{port}/api/{endpoint}")
                    collection = json.loads(response.decode("utf-8"))
                    self.assertEqual(status, 200)
                    self.assertEqual(collection.get("type"), "FeatureCollection")
                    self.assertGreater(len(collection.get("features", [])), minimum)
                    self.assertEqual(collection["features"][0]["geometry"]["type"], geometry)
        finally:
            if server.poll() is None:
                server.terminate()
            try:
                server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=3)
            server.communicate()

    def test_fgc_trains_and_lines_apis_keep_expected_structure(self):
        status, headers, body = fetch(FGC_TRAINS_API)
        geojson = json.loads(body.decode("utf-8"))
        self.assertEqual(status, 200)
        self.assertIn("json", headers.get("Content-Type", "").lower())
        self.assertEqual(geojson.get("type"), "FeatureCollection")
        self.assertTrue(geojson.get("features"), "FGC no ha publicado trenes en esta respuesta")
        self.assertTrue(
            all(feature.get("geometry", {}).get("type") == "Point" for feature in geojson["features"])
        )
        self.assertTrue(
            all(feature.get("properties", {}).get("id") for feature in geojson["features"]),
            "Se necesita un identificador estable para actualizar marcadores",
        )

        status, headers, body = fetch(FGC_LINES_API)
        lineas = json.loads(body.decode("utf-8"))
        self.assertEqual(status, 200)
        self.assertIn("json", headers.get("Content-Type", "").lower())
        self.assertIsInstance(lineas, list)
        self.assertTrue(lineas)
        codigos = {linea.get("route_id", "").upper() for linea in lineas}
        colores = [linea.get("route_color", "") for linea in lineas]
        self.assertTrue(codigos)
        self.assertTrue(all(re.fullmatch(r"[0-9a-fA-F]{6}", color) for color in colores if color))
        ids_trenes = {feature["properties"].get("lin", "").upper() for feature in geojson["features"]}
        self.assertGreaterEqual(len(ids_trenes & codigos), 1)

    def test_fgc_demo_matches_lesson_and_has_valid_javascript(self):
        lesson = (ROOT / "docs/19_ejemplo_fgc_realtime.md").read_text(encoding="utf-8")
        demo_path = FGC_EXAMPLE_DIR / "index.html"
        demo = demo_path.read_text(encoding="utf-8")
        self.assertIn("(ejemplos/fgc-trenes-realtime/index.html)", lesson)
        self.assertEqual(demo, code_block_after_heading(lesson, "## Código completo"))
        for expected in (
            "## 1. Explorar las API de FGC",
            "## 4. Consultar el GeoJSON y dibujar los trenes",
            "## 5. Actualizar posiciones y ventanas emergentes",
            "## Actividad breve en clase",
            "## Código completo",
        ):
            self.assertIn(expected, lesson)
        self.assertIn("setInterval(actualizarTrenes, INTERVALO_MS)", demo)
        self.assertIn("marcador.setLatLng(posicion)", demo)
        self.assertIn("marcadores.delete(id)", demo)
        self.assertIn("textContent", demo)

        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js no está instalado; se omite la comprobación de sintaxis JS")
        scripts = re.findall(r"<script>(.*?)</script>", demo, re.DOTALL)
        self.assertTrue(scripts, "No se encontró el código JavaScript del visor")
        result = subprocess.run(
            [node, "--check", "--input-type=commonjs"],
            input=scripts[-1],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_realtime_expedition_files_match_lesson_and_have_valid_javascript(self):
        lesson = (ROOT / "docs/17_ejemplo_geoservicio_realtime.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("(ejemplos/mapa-expedicion-realtime/preview.html)", lesson)
        for filename, heading, language in (
            ("server.js", "### Código de `server.js`", "js"),
            ("public/index.html", "### Código de `public/index.html`", "html"),
            ("public/app.js", "### Código de `public/app.js`", "js"),
        ):
            with self.subTest(file=filename):
                self.assertEqual(
                    (REALTIME_EXAMPLE_DIR / filename).read_text(encoding="utf-8"),
                    code_block_after_heading(lesson, heading),
                )

        for stage in (
            "### 1. Crear el mapa y el formulario de entrada",
            "### 2. Conectar el navegador con Socket.IO",
            "### 3. Registrar participantes y enviar el estado inicial",
            "### 4. Enviar la posición cuando alguien pulsa el mapa",
            "### 5. Mover el avatar y mostrar quién está conectado",
            "### 6. Instalar y ejecutar el servidor",
            "## Código completo",
        ):
            self.assertIn(stage, lesson)

        server = (REALTIME_EXAMPLE_DIR / "server.js").read_text(encoding="utf-8")
        app_code = (REALTIME_EXAMPLE_DIR / "public/app.js").read_text(encoding="utf-8")
        self.assertIn('"participants:snapshot"', server + app_code)
        self.assertIn('"participant:move"', server + app_code)
        self.assertIn('"participant:moved"', server + app_code)
        self.assertIn('socket.on("disconnect"', server)
        self.assertIn("marker.setLatLng(coordinates)", app_code)
        self.assertNotIn("navigator.geolocation", app_code)

        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js no está instalado; se omite la comprobación de sintaxis JS")

        for filename in ("server.js", "public/app.js"):
            with self.subTest(syntax=filename):
                result = subprocess.run(
                    [node, "--check", str(REALTIME_EXAMPLE_DIR / filename)],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_realtime_expedition_server_broadcasts_and_removes_participants(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js no está instalado; se omite la prueba de integración Socket.IO")

        client_check = subprocess.run(
            [node, "-e", "require.resolve('socket.io-client')"],
            cwd=REALTIME_EXAMPLE_DIR,
            capture_output=True,
            text=True,
        )
        if client_check.returncode != 0:
            self.skipTest(
                "Instala las dependencias del ejemplo con npm install para probar Socket.IO"
            )

        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]

        environment = os.environ.copy()
        environment.update({"PORT": str(port), "HOST": "127.0.0.1"})
        server = subprocess.Popen(
            [node, str(REALTIME_EXAMPLE_DIR / "server.js")],
            cwd=REALTIME_EXAMPLE_DIR,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if server.poll() is not None:
                    output = server.communicate()[0]
                    self.fail(f"El servidor de la expedición terminó al iniciar:\n{output}")
                try:
                    status, headers, body = fetch(f"http://127.0.0.1:{port}/")
                    break
                except URLError:
                    time.sleep(0.1)
            else:
                self.fail("El servidor de la expedición no respondió en 10 segundos")

            self.assertEqual(status, 200)
            self.assertIn("text/html", headers.get("Content-Type", "").lower())
            self.assertIn(b"Expedici\xc3\xb3n urbana", body)

            client_script = r"""
const assert = require("node:assert/strict");
const { io } = require("socket.io-client");
const url = process.env.REALTIME_TEST_URL;

function waitFor(socket, eventName, predicate = () => true) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`Timeout esperando ${eventName}`)), 5000);
    const listener = (value) => {
      if (!predicate(value)) return;
      clearTimeout(timer);
      socket.off(eventName, listener);
      resolve(value);
    };
    socket.on(eventName, listener);
  });
}

async function connectClient() {
  const socket = io(url, { autoConnect: false });
  const connected = waitFor(socket, "connect");
  const snapshot = waitFor(socket, "participants:snapshot");
  socket.connect();
  await connected;
  return { socket, initial: await snapshot };
}

async function join(socket, profile, participantCount) {
  const snapshot = waitFor(socket, "participants:snapshot", (list) => list.length === participantCount);
  const result = await new Promise((resolve) => socket.emit("participant:join", profile, resolve));
  assert.equal(result.ok, true);
  await snapshot;
  return result.id;
}

async function main() {
  const first = await connectClient();
  assert.deepEqual(first.initial, []);
  const firstId = await join(first.socket, { name: "Alba", avatar: "🦊" }, 1);

  const second = await connectClient();
  assert.equal(second.initial.length, 1, "Quien llega tarde recibe el estado actual");
  assert.equal(second.initial[0].id, firstId);

  const firstSnapshot = waitFor(first.socket, "participants:snapshot", (list) => list.length === 2);
  const secondSnapshot = waitFor(second.socket, "participants:snapshot", (list) => list.length === 2);
  const secondId = await join(second.socket, { name: "Marc", avatar: "🐼" }, 2);
  await Promise.all([firstSnapshot, secondSnapshot]);

  const moveAtSecond = waitFor(second.socket, "participant:moved", (participant) => participant.id === firstId);
  first.socket.emit("participant:move", { lat: 41.39, lng: 2.18 });
  const moved = await moveAtSecond;
  assert.equal(moved.position.lat, 41.39);
  assert.equal(moved.position.lng, 2.18);

  const oneParticipantLeft = waitFor(second.socket, "participants:snapshot", (list) => list.length === 1);
  first.socket.disconnect();
  const afterDisconnect = await oneParticipantLeft;
  assert.equal(afterDisconnect[0].id, secondId);

  second.socket.disconnect();
  process.stdout.write("Socket.IO: snapshot, entrada tardía, movimiento compartido y desconexión OK\n");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
"""
            client_environment = environment.copy()
            client_environment["REALTIME_TEST_URL"] = f"http://127.0.0.1:{port}"
            result = subprocess.run(
                [node, "-e", client_script],
                cwd=REALTIME_EXAMPLE_DIR,
                env=client_environment,
                capture_output=True,
                text=True,
                timeout=25,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("movimiento compartido", result.stdout)
        finally:
            if server.poll() is None:
                server.terminate()
            try:
                server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=3)
            server.communicate()

if __name__ == "__main__":
    unittest.main(verbosity=2)
