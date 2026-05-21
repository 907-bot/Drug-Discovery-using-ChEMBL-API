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