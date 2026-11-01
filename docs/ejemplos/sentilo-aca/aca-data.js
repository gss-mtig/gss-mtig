function catalogToGeoJSON(catalog) {
  const provider = catalog?.providers?.find(
    (item) => item.provider === "EMBASSAMENT-EST",
  );

  if (!provider) {
    throw new Error("El catálogo no contiene el proveedor EMBASSAMENT-EST.");
  }

  const stations = new Map();

  for (const sensor of provider.sensors || []) {
    const coordinates = String(sensor.location || "")
      .trim()
      .split(/\s+/)
      .map(Number);
    const [latitude, longitude] = coordinates;
    const component = sensor.component;

    if (
      coordinates.length !== 2 ||
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude) ||
      latitude < 40 || latitude > 43 ||
      longitude < 0 || longitude > 4 ||
      !component ||
      !sensor.sensor
    ) {
      continue;
    }

    if (!stations.has(component)) {
      stations.set(component, {
        type: "Feature",
        properties: {
          provider: provider.provider,
          component,
          name: sensor.componentDesc || component,
          sensors: [],
        },
        geometry: {
          type: "Point",
          coordinates: [longitude, latitude],
        },
      });
    }

    stations.get(component).properties.sensors.push({
      id: sensor.sensor,
      description: sensor.description || sensor.type || "Medida",
      unit: sensor.unit || "",
    });
  }

  return {
    type: "FeatureCollection",
    features: Array.from(stations.values()),
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { catalogToGeoJSON };
} else {
  window.AcaSentilo = { catalogToGeoJSON };
}
