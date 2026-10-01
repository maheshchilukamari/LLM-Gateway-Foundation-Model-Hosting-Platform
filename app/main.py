"""FastAPI application factory."""

# ruff: noqa: E501

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from app.api.middleware.request_context import request_context_middleware
from app.api.routes import admin, gateway, health, models
from app.core.config import get_settings
from app.core.exceptions import GatewayError
from app.core.logging import configure_logging, get_logger
from app.observability.metrics import metrics_response
from app.schemas.responses import ErrorResponse

DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LLM Gateway Platform</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #08111f;
      --panel: #101b2e;
      --panel-2: #13233a;
      --line: #26364d;
      --text: #eef5ff;
      --muted: #9fb1c7;
      --accent: #38bdf8;
      --accent-2: #22c55e;
      --warn: #f59e0b;
      --danger: #fb7185;
      --shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at 12% 0%, rgba(56, 189, 248, 0.20), transparent 30%),
        radial-gradient(circle at 88% 8%, rgba(34, 197, 94, 0.12), transparent 26%),
        linear-gradient(180deg, #091525 0%, var(--bg) 44%, #07101c 100%);
    }

    a { color: inherit; text-decoration: none; }

    .shell {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 56px;
    }

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 28px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }

    .mark {
      width: 44px;
      height: 44px;
      display: grid;
      place-items: center;
      border-radius: 10px;
      background: linear-gradient(135deg, #38bdf8, #22c55e);
      color: #06121f;
      font-weight: 900;
      box-shadow: var(--shadow);
    }

    .brand strong {
      display: block;
      font-size: 17px;
      line-height: 1.2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .brand span {
      display: block;
      margin-top: 2px;
      color: var(--muted);
      font-size: 13px;
    }

    .nav {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .nav a,
    button {
      border: 1px solid var(--line);
      background: #122033;
      color: var(--text);
      border-radius: 8px;
      padding: 10px 13px;
      font-weight: 700;
      cursor: pointer;
    }

    .nav a:hover,
    button:hover {
      border-color: var(--accent);
      background: #162942;
    }

    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.18fr) minmax(340px, 0.82fr);
      gap: 18px;
      align-items: stretch;
      margin-bottom: 18px;
    }

    .hero-main,
    .panel,
    .metric,
    .flow-step {
      border: 1px solid rgba(148, 163, 184, 0.18);
      background: rgba(16, 27, 46, 0.82);
      box-shadow: var(--shadow);
      backdrop-filter: blur(14px);
    }

    .hero-main {
      min-height: 360px;
      border-radius: 14px;
      padding: 34px;
      position: relative;
      overflow: hidden;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: #b9ecff;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0;
      text-transform: uppercase;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--accent-2);
      box-shadow: 0 0 22px rgba(34, 197, 94, 0.9);
    }

    h1 {
      margin: 18px 0 14px;
      max-width: 760px;
      font-size: clamp(34px, 5vw, 62px);
      line-height: 1.02;
      letter-spacing: 0;
    }

    .hero-main p {
      max-width: 720px;
      color: var(--muted);
      font-size: 17px;
      line-height: 1.65;
      margin: 0 0 24px;
    }

    .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 20px;
    }

    .primary {
      border-color: transparent;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      color: #06121f;
    }

    .status-board {
      border-radius: 14px;
      padding: 22px;
      display: grid;
      gap: 14px;
      background:
        linear-gradient(180deg, rgba(19, 35, 58, 0.95), rgba(12, 23, 39, 0.96));
      border: 1px solid rgba(148, 163, 184, 0.20);
      box-shadow: var(--shadow);
    }

    .status-line {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--line);
    }

    .status-line span {
      color: var(--muted);
      font-size: 13px;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      border-radius: 999px;
      padding: 7px 10px;
      color: #bbf7d0;
      background: rgba(34, 197, 94, 0.12);
      border: 1px solid rgba(34, 197, 94, 0.35);
      font-size: 13px;
      font-weight: 800;
      white-space: nowrap;
    }

    .metrics {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }

    .metric {
      border-radius: 10px;
      padding: 16px;
      background: rgba(8, 17, 31, 0.56);
    }

    .metric b {
      display: block;
      font-size: 26px;
      line-height: 1;
      margin-bottom: 8px;
    }

    .metric span {
      color: var(--muted);
      font-size: 13px;
    }

    .section-title {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 18px;
      margin: 34px 0 14px;
    }

    .section-title h2 {
      margin: 0;
      font-size: 24px;
    }

    .section-title p {
      margin: 0;
      color: var(--muted);
      max-width: 580px;
      line-height: 1.5;
    }

    .grid-3 {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }

    .panel {
      border-radius: 12px;
      padding: 20px;
      background: rgba(16, 27, 46, 0.80);
    }

    .panel h3 {
      margin: 0 0 8px;
      font-size: 17px;
    }

    .panel p,
    .panel li {
      color: var(--muted);
      line-height: 1.55;
      font-size: 14px;
    }

    .panel ul {
      margin: 12px 0 0;
      padding-left: 18px;
    }

    .demo {
      display: grid;
      grid-template-columns: minmax(320px, 0.9fr) minmax(0, 1.1fr);
      gap: 14px;
    }

    label {
      display: block;
      margin: 12px 0 7px;
      color: #d7e5f7;
      font-size: 13px;
      font-weight: 800;
    }

    input,
    select,
    textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0a1525;
      color: var(--text);
      padding: 12px;
      font: inherit;
      resize: vertical;
    }

    textarea { min-height: 112px; }

    .result {
      min-height: 362px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #07101d;
      padding: 16px;
      overflow: auto;
      white-space: pre-wrap;
      color: #dbeafe;
      font-family: Consolas, ui-monospace, monospace;
      font-size: 13px;
      line-height: 1.55;
    }

    .flow {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
    }

    .flow-step {
      border-radius: 10px;
      padding: 16px;
      min-height: 118px;
      background: rgba(8, 17, 31, 0.62);
    }

    .flow-step b {
      display: block;
      margin-bottom: 8px;
      color: #e0f2fe;
    }

    .flow-step span {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .models {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 12px;
    }

    .model-card {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 16px;
      background: #0a1525;
    }

    .model-card b {
      display: block;
      margin-bottom: 8px;
      word-break: break-word;
    }

    .model-card span {
      display: inline-flex;
      margin: 4px 6px 0 0;
      padding: 5px 8px;
      border: 1px solid #29425f;
      border-radius: 999px;
      color: #bcd0e6;
      font-size: 12px;
    }

    footer {
      margin-top: 34px;
      color: var(--muted);
      font-size: 13px;
      text-align: center;
    }

    @media (max-width: 900px) {
      .hero,
      .demo,
      .grid-3,
      .flow {
        grid-template-columns: 1fr;
      }

      header,
      .section-title {
        align-items: flex-start;
        flex-direction: column;
      }

      .nav {
        justify-content: flex-start;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <a class="brand" href="/">
        <div class="mark">LLM</div>
        <div>
          <strong>__APP_NAME__</strong>
          <span>My university LLM infrastructure project</span>
        </div>
      </a>
      <nav class="nav" aria-label="Project links">
        <a href="/docs">API Docs</a>
        <a href="/v1/models">Models</a>
        <a href="/metrics">Metrics</a>
        <a href="/redoc">ReDoc</a>
      </nav>
    </header>

    <section class="hero">
      <div class="hero-main">
        <div class="eyebrow"><span class="dot"></span> Running locally on FastAPI</div>
        <h1>Unified LLM Gateway for routing, RAG, caching, and observability.</h1>
        <p>
          I built this project to show how production model platforms put a gateway
          between applications and foundation models. It includes model metadata, routing,
          local inference, RAG retrieval, cache behavior, metrics, security controls,
          Docker, Kubernetes, Helm, Terraform, and CI/CD scaffolding.
        </p>
        <div class="hero-actions">
          <a class="primary" href="#demo">Run Browser Demo</a>
          <a href="/docs">Open Swagger UI</a>
          <a href="/ready">Check Readiness</a>
        </div>
      </div>

      <aside class="status-board" aria-label="Live platform status">
        <div class="status-line">
          <div>
            <strong>Gateway Status</strong>
            <span id="statusText">Checking services...</span>
          </div>
          <div class="pill"><span class="dot"></span><span id="statusPill">LIVE</span></div>
        </div>
        <div class="metrics">
          <div class="metric"><b id="modelCount">-</b><span>Registered models</span></div>
          <div class="metric"><b>__API_VERSION__</b><span>API version</span></div>
          <div class="metric"><b id="cacheState">Ready</b><span>Local cache</span></div>
          <div class="metric"><b id="ragState">Ready</b><span>RAG pipeline</span></div>
        </div>
        <div class="panel">
          <h3>Presentation Mode</h3>
          <p>
            Use the browser demo below for a clean classroom walkthrough, then open
            Swagger UI to show the actual REST API contracts.
          </p>
        </div>
      </aside>
    </section>

    <section>
      <div class="section-title">
        <h2>Platform Capabilities</h2>
        <p>I designed it like a real model platform while keeping it runnable on a normal laptop.</p>
      </div>
      <div class="grid-3">
        <article class="panel">
          <h3>Gateway and Routing</h3>
          <p>One API selects models using latency, cost, quality, throughput, and resource-aware strategies.</p>
          <ul>
            <li>API-key authentication</li>
            <li>Request IDs and standard responses</li>
            <li>Model metadata and versioning</li>
          </ul>
        </article>
        <article class="panel">
          <h3>RAG and Inference</h3>
          <p>Local retrieval pipeline augments prompts with sources and sends them through the same gateway path.</p>
          <ul>
            <li>Chunking and vector search</li>
            <li>Embeddings endpoint</li>
            <li>Local provider plus Hugging Face adapter</li>
          </ul>
        </article>
        <article class="panel">
          <h3>Operations</h3>
          <p>I included the operational pieces needed to explain the system clearly in a project review.</p>
          <ul>
            <li>Prometheus metrics</li>
            <li>Docker, Kubernetes, Helm</li>
            <li>Alembic, Terraform, CI/CD</li>
          </ul>
        </article>
      </div>
    </section>

    <section id="demo">
      <div class="section-title">
        <h2>Live Gateway Demo</h2>
        <p>Run generation or RAG from this page. The calls go to the same protected API used by external clients.</p>
      </div>
      <div class="demo">
        <div class="panel">
          <label for="apiKey">API Key</label>
          <input id="apiKey" value="dev-api-key" autocomplete="off" />

          <label for="mode">Request Type</label>
          <select id="mode">
            <option value="generate">Text generation</option>
            <option value="rag">RAG query</option>
          </select>

          <label for="strategy">Routing Strategy</label>
          <select id="strategy">
            <option value="balanced">balanced</option>
            <option value="lowest_latency">lowest_latency</option>
            <option value="lowest_cost">lowest_cost</option>
            <option value="highest_quality">highest_quality</option>
            <option value="highest_throughput">highest_throughput</option>
            <option value="resource_aware">resource_aware</option>
          </select>

          <label for="prompt">Prompt</label>
          <textarea id="prompt">Explain why an LLM Gateway is useful for enterprise applications.</textarea>

          <div class="hero-actions">
            <button class="primary" id="runDemo" type="button">Run Request</button>
            <button id="cacheDemo" type="button">Run Twice for Cache</button>
          </div>
        </div>

        <div class="panel">
          <h3>Response</h3>
          <div id="result" class="result">Choose a request and run the demo.</div>
        </div>
      </div>
    </section>

    <section>
      <div class="section-title">
        <h2>Request Flow</h2>
        <p>The gateway keeps client applications separate from model-serving and policy complexity.</p>
      </div>
      <div class="flow">
        <div class="flow-step"><b>1. Gateway</b><span>FastAPI validates schema, API key, request ID, and limits.</span></div>
        <div class="flow-step"><b>2. Router</b><span>Selects a healthy model based on the requested strategy.</span></div>
        <div class="flow-step"><b>3. RAG or Provider</b><span>Optionally retrieves context, then invokes the model provider.</span></div>
        <div class="flow-step"><b>4. Observability</b><span>Returns standardized output with token, cost, cache, and metrics data.</span></div>
      </div>
    </section>

    <section>
      <div class="section-title">
        <h2>Registered Models</h2>
        <p>Loaded live from the YAML-backed model registry.</p>
      </div>
      <div id="models" class="models"></div>
    </section>

    <footer>
      Built as my university LLM platform project. Default mode uses deterministic local inference
      so the demo is reliable without downloading large models.
    </footer>
  </div>

  <script>
    const result = document.getElementById("result");
    const modelContainer = document.getElementById("models");

    async function api(path, options = {}) {
      const response = await fetch(path, options);
      const text = await response.text();
      let body;
      try { body = JSON.parse(text); } catch { body = text; }
      if (!response.ok) {
        throw new Error(JSON.stringify(body, null, 2));
      }
      return body;
    }

    async function loadStatus() {
      try {
        const [health, ready, models] = await Promise.all([
          api("/health"),
          api("/ready"),
          api("/v1/models")
        ]);
        document.getElementById("statusText").textContent =
          `${health.status.toUpperCase()} - ${ready.status}`;
        document.getElementById("modelCount").textContent = models.models.length;
        modelContainer.innerHTML = models.models.map((model) => `
          <article class="model-card">
            <b>${model.model_id}</b>
            <div>${model.provider} - ${model.task_type} - v${model.model_version}</div>
            <span>${model.health_status}</span>
            <span>${model.device}</span>
            <span>quality ${model.quality_score}</span>
          </article>
        `).join("");
      } catch (error) {
        document.getElementById("statusText").textContent = "Status check failed";
        result.textContent = error.message;
      }
    }

    function requestPayload() {
      const mode = document.getElementById("mode").value;
      const prompt = document.getElementById("prompt").value;
      const strategy = document.getElementById("strategy").value;
      if (mode === "rag") {
        return {
          path: "/v1/rag/query",
          body: {
            model: "auto",
            query: prompt,
            routing_strategy: strategy,
            top_k: 2,
            similarity_threshold: 0.0
          }
        };
      }
      return {
        path: "/v1/generate",
        body: {
          model: "auto",
          prompt,
          routing_strategy: strategy,
          max_tokens: 220
        }
      };
    }

    async function runOnce() {
      const { path, body } = requestPayload();
      const apiKey = document.getElementById("apiKey").value;
      result.textContent = "Running request...";
      const response = await api(path, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey
        },
        body: JSON.stringify(body)
      });
      result.textContent = JSON.stringify(response, null, 2);
      return response;
    }

    document.getElementById("runDemo").addEventListener("click", async () => {
      try { await runOnce(); } catch (error) { result.textContent = error.message; }
    });

    document.getElementById("cacheDemo").addEventListener("click", async () => {
      try {
        result.textContent = "Running first request...";
        const first = await runOnce();
        result.textContent = "Running second identical request...";
        const second = await runOnce();
        result.textContent = JSON.stringify({ first, second }, null, 2);
      } catch (error) {
        result.textContent = error.message;
      }
    });

    loadStatus();
  </script>
</body>
</html>
"""


def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Production-style LLM Gateway and foundation model hosting platform.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.middleware("http")(request_context_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(models.router)
    app.include_router(gateway.router)
    app.include_router(admin.router)
    app.add_api_route("/metrics", metrics_response, methods=["GET"], tags=["observability"])

    @app.get("/", response_class=HTMLResponse, tags=["root"])
    async def root() -> str:
        """Return a polished browser dashboard for university demos."""
        return DASHBOARD_HTML.replace("__APP_NAME__", settings.app_name).replace(
            "__API_VERSION__",
            settings.api_version,
        )

    @app.exception_handler(GatewayError)
    async def gateway_error_handler(request: Request, exc: GatewayError) -> JSONResponse:
        logger.warning("gateway_error", error_type=exc.__class__.__name__)
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                request_id=getattr(request.state, "request_id", None),
                error=exc.__class__.__name__,
                detail=str(exc),
            ).model_dump(),
        )

    return app


app = create_app()
