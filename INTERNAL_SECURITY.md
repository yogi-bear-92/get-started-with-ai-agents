# Internal Security & Escalation

This repository is private. Follow these guidelines to protect credentials, data, and infrastructure.

## Contacts / Escalation
| Area | Primary | Backup | Channel |
|------|---------|--------|---------|
| Security Review / Threat Modeling | security-lead@example.com | dev-lead@example.com | Teams: #sec-ai-agent |
| Incident Response (Off Hours) | oncall-sre@example.com | oncall-manager@example.com | Pager rotation |
| Credential Management / Key Vault | platform-eng@example.com | devops@example.com | Teams: #platform |
| Azure Cost / Quota | finops@example.com | finops-backup@example.com | Email DL: finops@example.com |

(Replace placeholder emails with real internal contacts.)

## Secrets & Identity
- Use managed identity wherever possible; avoid embedding keys.
- Never commit `.env` files containing secrets.
- Rotate any shared credentials at least every 90 days.

## Logging & Data Handling
- Avoid logging PII or secrets; sanitize user inputs before logging.
- Red team and evaluation outputs may contain sensitive model behavior; store under restricted access.

## Change Management
- Require peer review for changes touching `infra/`, auth flows, or evaluation safety logic.
- Pin critical dependencies; review diff of `pip install --dry-run` when upgrading security-sensitive libs.

## Dependency Monitoring
- Run `pip list --outdated` monthly and assess security advisories (e.g., dependabot or internal tooling).
- Prioritize patches for: `fastapi`, `uvicorn`, `azure-*`, cryptography libs.

## Deployment Safeguards
- Use `azd up` only from approved branches (main or release/*).
- Validate environment variables with `scripts/validate_env_vars.sh` prior to deploy.

## Incident Response Playbook (Abbreviated)
1. Triage: Identify scope (service, data, credentials).
2. Contain: Revoke keys / disable affected agent or service.
3. Eradicate: Patch vulnerability / revert malicious change.
4. Recover: Redeploy clean artifacts; re-enable monitored endpoints.
5. Postmortem: Document root cause & preventative actions.

## Hardening Backlog (Suggest)
- Add automatic secret scanning in CI.
- Implement role-based authorization guards in API routes.
- Integrate Azure Monitor alerts for anomalous token usage.
- Add signed container image verification.

## Classification
All repository contents: INTERNAL USE ONLY. Do not redistribute externally without security approval.
