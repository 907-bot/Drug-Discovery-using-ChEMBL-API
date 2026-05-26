# ChEMBL Discovery Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Version-1.0.0-purple" alt="Version">
</p>

Enterprise-grade pharmaceutical research platform for drug discovery using the ChEMBL bioactivity database. Production-ready with FastAPI, comprehensive testing, and Docker deployment.

## Features

- **Disease-based drug search** - Find drugs indicated for any disease using EFO terms
- **Target-based discovery** - Search by protein target and organism
- **Drug comparison** - Side-by-side comparison of multiple compounds
- **Approval status** - Check FDA approval status for any compound
- **RESTful API** - Full FastAPI service with OpenAPI docs
- **Type-safe** - Complete type hints and validation
- **Production-ready** - Docker, CI/CD, testing built-in

## Quick Start

```python
# Install
pip install chembldiscovery

# Use the library
from chembldiscovery import DrugService

service = DrugService()
result = service.search_by_disease("dengue")

for drug in result.drugs:
    print(f"{drug.drug_name}: Phase {drug.max_phase}")
```

## API Usage

```bash
# Start the API server
uvicorn chembldiscovery.api.main:app --reload

# Search for drugs
curl "http://localhost:8000/api/v1/drugs/search?disease=cancer&max_results=10"

# Get drug details
curl "http://localhost:8000/api/v1/drugs/CHEM126921"

# Check approval
curl "http://localhost:8000/api/v1/drugs/CHEM126921/approved"
```

## Docker Deployment

```bash
# Build and run
docker build -t chembldiscovery .
docker run -p 8000:8000 chembldiscovery

# Or use docker-compose
docker-compose up -d
```

## Architecture

```
chembldiscovery/
├── src/chembldiscovery/
│   ├── api/          # FastAPI routes
│   ├── core/         # ChEMBL client
│   ├── models/      # Data models
│   └── services/    # Business logic
├── tests/            # Test suite
├── config/           # Configuration
└── .github/         # CI/CD workflows
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /api/v1/drugs/search` | Search by disease |
| `GET /api/v1/drugs/{chembl_id}` | Drug details |
| `GET /api/v1/drugs/{chembl_id}/approved` | Check approval |
| `GET /api/v1/targets/search` | Search targets |
| `POST /api/v1/drugs/compare` | Compare drugs |

## Development

```bash
# Clone and install
git clone https://github.com/chembldiscovery/chembldiscovery.git
cd chembldiscovery
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint
ruff check src/
mypy src/
```

## Tech Stack

- **ChEMBL WebResource Client** - Database access
- **RDKit** - Molecular processing
- **FastAPI** - REST API
- **Pydantic** - Validation
- **Pytest** - Testing
- **Docker** - Deployment

## License

MIT License - See LICENSE file.

## Citation

If you use this software in research, please cite:

```bibtex
@software{chembldiscovery2025,
  title = {ChEMBL Discovery Platform},
  author = {ChEMBL Discovery Team},
  year = {2025},
  url = {https://github.com/chembldiscovery/chembldiscovery}
}
```

## 🌐 Deploy Frontend (Landing Page)

### Option 1: Vercel (Recommended - Free)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project folder
cd /workspace/project/Drug-Discovery-using-ChEMBL-API
vercel
```

### Option 2: Netlify (Free)

```bash
# Drag & drop index.html to netlify.com/drop
# Or connect GitHub repo
```

### Option 3: GitHub Pages

```bash
# Create gh-pages branch
git subtree push --prefix=. origin gh-pages
```

### Option 4: Cloudflare Pages (Free)

1. Go to dash.cloudflare.com/pages
2. Connect GitHub repo
3. Build output: `.`
4. Deploy!

---

### 🎯 Connect Frontend to Backend

After deploying both services:

1. **Update API URL in index.html:**
```javascript
// Line ~367 in index.html
const API_BASE = 'https://chembldiscovery.onrender.com'; // Your Render URL
```

2. **Enable CORS on Backend:**
The API already has CORS enabled for all origins.

3. **Test:**
- Frontend: `https://your-frontend.vercel.app`
- Backend: `https://your-backend.onrender.com`
- API Docs: `https://your-backend.onrender.com/docs`

---

### Current Architecture

| Component | Where | URL |
|----------|-------|-----|
| Frontend | Vercel/Netlify | `*.vercel.app` |
| Backend API | Render | `*.onrender.com` |
| Database | ChEMBL (external) | `ftp.ebi.ac.uk` |
```

## 🚀 Deploy to Render (Free)

### Option 1: Push to GitHub & Connect to Render

1. **Push code to GitHub:**
```bash
git add -A
git commit -m "Add Render deployment"
git push origin main
```

2. **Deploy on Render:**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Build Command**: `pip install -e .`
     - **Start Command**: `uvicorn chembldiscovery.api.main:app --host 0.0.0.0 --port $PORT`
   - Click "Create Web Service"

### Option 2: Using Docker on Render

```bash
# Build and push Docker image
docker build -t chembldiscovery .
docker tag chembldiscovery:latest yourusername/chembldiscovery:latest
docker push yourusername/chembldiscovery:latest
```

Then on Render, use the Docker image.

### Environment Variables (Optional)

Set these in Render dashboard:
- `PORT` = `8000` (default)
- `PYTHON_VERSION` = `3.12`

### Test Your Deployment

```bash
curl https://your-app.onrender.com/health
# Returns: {"status":"healthy","version":"1.0.0"}

curl https://your-app.onrender.com/docs
# Interactive API documentation
```

### Free Tier Limits

- 750 hours/month (automatic sleep after 15 min inactivity)
- Shared CPU
- 512 MB RAM
- Enough for demos and testing
```