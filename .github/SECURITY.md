# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please **do not** open a public GitHub issue.

Instead, report it privately by:

1. **Email:** Open a private GitHub security advisory at  
   `https://github.com/HolyCrossGleam7/community-credit-mesh/security/advisories/new`
2. **Include in your report:**
   - A description of the vulnerability and its potential impact
   - Steps to reproduce the issue
   - Affected files, versions, or components
   - Any suggested remediation (optional)

We aim to acknowledge reports within **72 hours** and provide a fix or mitigation plan within **14 days** for critical issues.

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` branch | ✅ Yes |
| Older releases | ❌ No — please update |

## Security Review Schedule

This project runs an automated monthly security review via GitHub Actions  
(`.github/workflows/security-review.yml`) covering:

- Python static analysis (Bandit)
- Dependency vulnerability scanning (pip-audit)
- Hardcoded secret detection (detect-secrets)

A tracking issue is automatically opened on the first day of each month.  
See [SECURITY.md](../SECURITY.md) for full findings and recommendations.

## Scope

This policy covers:

- **Desktop application** (`community-credit-mesh` — this repository)
- **Mobile PWA** (`community-credit-mesh-pwa` — https://github.com/HolyCrossGleam7/community-credit-mesh-pwa)
