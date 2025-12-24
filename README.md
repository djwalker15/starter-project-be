# FastAPI Starter (Cloud Run Ready)

A minimal FastAPI starter repository designed for quick project bootstraps.

## Features
- FastAPI app with versioned API (`/api/v1`) and stub endpoints
- Local run (hot reload) via `uvicorn` or Docker
- Test suite with **unit** and **integration** tests (pytest + httpx via ASGITransport)
- Linting/formatting/type-checking: ruff, black, mypy
- GitHub Actions CI: lint + tests
- GitHub Actions Deploy (optional) to Google Cloud Run
- 12-factor style config with `.env`
- **requirements.txt** and **requirements-dev.txt** (instead of using `pyproject` for deps)

---

## Quickstart

### 1) Python environment
```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate  # Windows PowerShell

pip install -U pip
pip install -r requirements-dev.txt
cp .env.example .env
make run   # http://127.0.0.1:8000/docs
```

### 2) Docker (local)
```bash
docker build -t fastapi-starter:local .
docker run --rm -p 8000:8080 --env-file .env fastapi-starter:local
```

### 3) Run tests & quality checks
```bash
make qa      # ruff + black + mypy + pytest
make test    # pytest
make cov     # coverage report
```

---

## Endpoints (stubs)
- `GET /health` – healthcheck
- `GET /version` – app version
- `GET /api/v1/items` – list items (stub, in-memory)
- `POST /api/v1/echo` – echoes a payload (stub)

Interactive docs at `/docs` and `/redoc`.

---

## Configuration
Configuration is managed via environment variables (see `app/core/config.py`) and `.env` file.

Key variables:
- `APP_NAME` (default: `fastapi-starter`)
- `APP_VERSION` (default: `0.1.0`)
- `ENV` (default: `local`)
- `LOG_LEVEL` (default: `INFO`)
- `PORT` (default: `8080` for container; `8000` for local dev with `make run`)

---

## Deploy to Google Cloud Run

### Prereqs
- Google Cloud project & billing enabled
- Artifact Registry repo (or Docker Hub alternative)
- `gcloud` CLI installed and authenticated
- Enable services:
  ```bash
  gcloud services enable run.googleapis.com artifactregistry.googleapis.com
  ```

### Build & Push image (Artifact Registry)
```bash
REGION="us-central1"           # change as needed
PROJECT_ID="your-gcp-project"  # change
REPO="apps"                    # your Artifact Registry repo name
IMAGE="fastapi-starter"

gcloud auth configure-docker ${REGION}-docker.pkg.dev
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE}:v1 .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE}:v1
```

### Deploy
```bash
SERVICE="fastapi-starter"
REGION="us-central1"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE}:v1"

gcloud run deploy ${SERVICE}   --image=${IMAGE_URI}   --region=${REGION}   --platform=managed   --allow-unauthenticated   --port=8080   --min-instances=0   --max-instances=5   --set-env-vars=ENV=prod,LOG_LEVEL=INFO,APP_NAME=fastapi-starter
```

---

## Project Layout
```
app/
  api/
    v1/routes.py
  core/config.py
  main.py
tests/
  unit/
    test_health.py
    test_config.py
  integration/
    test_endpoints.py
.github/workflows/
  ci.yml
  deploy.yml           # optional (edit before enabling)
scripts/
  dev.sh
Dockerfile
docker-compose.yml
pyproject.toml         # tool configs only (ruff/black/mypy/pytest)
requirements.txt
requirements-dev.txt
Makefile
.env.example
```
