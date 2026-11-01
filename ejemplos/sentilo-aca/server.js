const express = require("express");

const app = express();
const port = process.env.PORT || 3000;
const acaApi = "https://aplicacions.aca.gencat.cat/sdim2/apirest";

app.use(express.static(__dirname));

app.get("/api/catalog", async (_request, response) => {
  await forwardJson(
    `${acaApi}/catalog?componentType=embassament`,
    response,
  );
});

app.get("/api/data/:provider/:sensor", async (request, response) => {
  const { provider, sensor } = request.params;
  const validId = /^[A-Za-z0-9_-]+$/;

  if (!validId.test(provider) || !validId.test(sensor)) {
    response.status(400).json({ error: "Identificador no válido." });
    return;
  }

  const url = `${acaApi}/data/${encodeURIComponent(provider)}/${encodeURIComponent(sensor)}`;
  await forwardJson(url, response);
});

async function forwardJson(url, response) {
  try {
    const acaResponse = await fetch(url, {
      headers: { Accept: "application/json" },
    });
    const body = await acaResponse.text();
    const contentType = acaResponse.headers.get("content-type");

    response.status(acaResponse.status);
    if (contentType) response.set("content-type", contentType);
    response.send(body);
  } catch (error) {
    console.error("No se pudo consultar la API de la ACA:", error);
    response.status(502).json({ error: "No se pudo consultar la API de la ACA." });
  }
}

app.listen(port, () => {
  console.log(`Visor disponible en http://localhost:${port}`);
});
