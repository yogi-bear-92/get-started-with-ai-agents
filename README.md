## Internal AI Agent Platform (Private Repository)

This repository contains an internal AI agent application built on Azure AI services (Agents, Search, Monitoring). It is now private; all public-facing artifacts (license, contribution guidelines, code of conduct, security policy) have been removed per instruction.

### Purpose
Provide a customizable chat + retrieval + evaluation stack for internal experimentation, prototyping, and integration with downstream services.

### High-Level Components
- FastAPI backend (`src/api`) exposing chat, memory, search, evaluation hooks
- Agent configuration & tools (`gunicorn.conf.py`)
- Retrieval: vector + keyword memory plus optional Azure AI Search index management
- Evaluation & red teaming utilities (`evals/`, `airedteaming/`)
- Frontend React app (under `src/frontend`) served via FastAPI static build

### Quick Start (Internal)
```bash
azd up                # First-time infra + deploy (ensure correct subscription)
source .venv/bin/activate || python -m venv .venv && source .venv/bin/activate
pip install -r src/requirements-dev.txt
python -m uvicorn "api.main:create_app" --factory --reload --app-dir src
```

Set required environment variables (see `azure.yaml`). Use `azd env set KEY VALUE` to persist.

### Common Env Vars
- AZURE_AI_AGENT_MODEL_NAME
- AZURE_AI_AGENT_MODEL_FORMAT
- AZURE_AI_PROJECT_NAME / LOCATION
- USE_AZURE_AI_SEARCH_SERVICE (true/false)

### Development Notes
- Update knowledge files in `src/files/` BEFORE (re)creating an agent.
- Changing files after creation requires deleting & recreating the agent resource.
- For evaluation/red teaming, ensure the `azure-ai-evaluation[redteam]` dependency is installed (already in requirements).

### Testing
```bash
pytest -q
```
Some tests require Azure resources / credentials; set appropriate connection strings or mark them skipped internally if unavailable.

### Deployment
Use `azd deploy` after changes to push container image and update resources. For full reprovisioning or teardown: `azd down` (destroys resources).

### Security / Compliance (Internal)
- Secrets are expected to be managed via Azure Developer CLI environment or managed identity.
- Do NOT add plaintext credentials to the repo.
- Review access controls on the private repo periodically.

### Directory Pointers
| Path | Purpose |
|------|---------|
| `src/api` | FastAPI app + agent integration |
| `src/files` | Knowledge ingestion files (must exist before agent creation) |
| `evals/` | Evaluation scripts & config |
| `airedteaming/` | Automated red teaming script(s) |
| `infra/` | Bicep templates for Azure provisioning |
| `docs/` | Internal technical docs (retain only non-public sensitive info) |

### Internal Maintenance
- Keep dependencies patched (focus on azure-* libs, fastapi, uvicorn).
- Run evaluation & red team scripts before major merges.
- Remove any reintroduced notebooks unless intentionally required (policy: notebooks allowed now but discouraged in main branch).

### Disclaimer (Internal Use Only)
This code is provided for internal experimentation. Not hardened for external distribution or production without additional security review, monitoring, cost controls, and compliance validation.

---
Minimal public artifacts have been removed as requested.
