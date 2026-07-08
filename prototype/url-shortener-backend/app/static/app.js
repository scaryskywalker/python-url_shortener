const output = document.querySelector("#output");
const apiKeyInput = document.querySelector("#apiKey");
const strategySelect = document.querySelector("#strategySelect");
const configSelect = document.querySelector("#configSelect");
const strategyIdInput = document.querySelector("#strategyId");
const configIdInput = document.querySelector("#configId");
const shortUrlLink = document.querySelector("#shortUrl");

let lastShortCode = "";

function show(data) {
  output.textContent = JSON.stringify(data, null, 2);
}

function setStatus(id, value, ok) {
  const element = document.querySelector(id);
  element.textContent = value;
  element.className = ok ? "ok" : "bad";
}

function formJson(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  if ("output_length" in data) {
    data.output_length = Number(data.output_length);
  }
  if ("is_active" in data) {
    data.is_active = form.elements.is_active.checked;
  }
  if (data.valid_until) {
    data.valid_until = new Date(data.valid_until).toISOString();
  }
  return data;
}

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(path, { ...options, headers });
  const text = await response.text();
  let data = {};
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }
  }
  if (!response.ok) {
    throw { status: response.status, data };
  }
  return data;
}

function authHeaders() {
  const apiKey = apiKeyInput.value.trim();
  if (!apiKey) {
    throw { status: 401, data: { detail: "Paste or create an API key first" } };
  }
  return { "X-API-Key": apiKey };
}

async function checkHealth() {
  try {
    const data = await request("/health");
    setStatus("#apiStatus", data.status, data.status === "ok");
    setStatus("#mysqlStatus", data.mysql, data.mysql === "ok");
    setStatus("#redisStatus", data.redis, data.redis === "ok");
    show(data);
  } catch (error) {
    setStatus("#apiStatus", "error", false);
    setStatus("#mysqlStatus", "unknown", false);
    setStatus("#redisStatus", "unknown", false);
    show(error);
  }
}

async function loadStrategies() {
  const data = await request("/api/v1/strategies");
  strategySelect.innerHTML = "";
  for (const strategy of data) {
    const option = document.createElement("option");
    option.value = strategy.strategy_id;
    option.textContent = `${strategy.name} | ${strategy.output_length} | ${strategy.strategy_id}`;
    strategySelect.append(option);
  }
  show(data);
}

async function loadConfigs() {
  const data = await request("/api/v1/configs", { headers: authHeaders() });
  configSelect.innerHTML = "";
  for (const config of data) {
    const option = document.createElement("option");
    option.value = config.config_id;
    option.textContent = `${config.is_active ? "active" : "inactive"} | ${config.valid_until} | ${config.config_id}`;
    configSelect.append(option);
  }
  show(data);
}

document.querySelector("#healthButton").addEventListener("click", checkHealth);
document.querySelector("#loadStrategiesButton").addEventListener("click", () => loadStrategies().catch(show));

document.querySelector("#merchantForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const data = await request("/api/v1/merchants", {
      method: "POST",
      body: JSON.stringify(formJson(event.currentTarget)),
    });
    apiKeyInput.value = data.api_key;
    show(data);
  } catch (error) {
    show(error);
  }
});

document.querySelector("#strategyForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const data = await request("/api/v1/strategies", {
      method: "POST",
      body: JSON.stringify(formJson(event.currentTarget)),
    });
    show(data);
    await loadStrategies();
  } catch (error) {
    show(error);
  }
});

document.querySelector("#configForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const data = await request("/api/v1/configs", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(formJson(event.currentTarget)),
    });
    configIdInput.value = data.config_id;
    show(data);
    await loadConfigs();
  } catch (error) {
    show(error);
  }
});

document.querySelector("#shortenForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const data = await request("/api/v1/urls/shorten", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(formJson(event.currentTarget)),
    });
    lastShortCode = data.short_code;
    shortUrlLink.href = data.short_url;
    shortUrlLink.textContent = data.short_url;
    show(data);
  } catch (error) {
    show(error);
  }
});

document.querySelector("#validateButton").addEventListener("click", async () => {
  try {
    if (!lastShortCode) {
      throw { status: 400, data: { detail: "Generate a short URL first" } };
    }
    show(await request(`/api/v1/urls/${lastShortCode}/validate`));
  } catch (error) {
    show(error);
  }
});

document.querySelector("#openShortButton").addEventListener("click", () => {
  if (lastShortCode) {
    window.open(`/${lastShortCode}`, "_blank", "noopener,noreferrer");
  }
});

strategySelect.addEventListener("change", () => {
  strategyIdInput.value = strategySelect.value;
});

configSelect.addEventListener("change", () => {
  configIdInput.value = configSelect.value;
});

const nextYear = new Date();
nextYear.setFullYear(nextYear.getFullYear() + 1);
document.querySelector("#validUntil").value = nextYear.toISOString().slice(0, 16);
document.querySelector('input[name="merchant_code"]').value = `PROTECHY${Date.now().toString().slice(-6)}`;

checkHealth().then(loadStrategies).catch(show);
