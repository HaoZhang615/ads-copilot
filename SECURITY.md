# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in ADS Copilot, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please email the maintainer directly:

1. Send an email describing the vulnerability to the repository owner (see GitHub profile)
2. Include steps to reproduce the issue
3. Provide your assessment of the severity
4. Allow up to 72 hours for an initial response

## Scope

The following are in scope for security reports:

- Authentication and authorization bypasses in the WebSocket endpoint
- Credential leakage (API keys, Azure tokens) in logs or responses
- Server-side request forgery (SSRF) via MCP server integration
- Cross-site scripting (XSS) in the chat interface
- Injection attacks through voice transcription text
- Insecure default configurations in `.env.sample` or Bicep templates

## Out of Scope

- Vulnerabilities in upstream dependencies (report those to the dependency maintainers)
- Denial of service through normal API rate limiting
- Issues that require physical access to the deployment

## Supported Versions

| Version | Supported |
|---------|-----------|
| `voicelive-app` branch (latest) | ✅ |
| All other branches | ❌ |

## Security Best Practices for Deployment

When deploying ADS Copilot:

- Never commit `.env` files — use `.env.sample` as a template
- Use Azure Key Vault for all secrets (the `azd up` flow does this automatically)
- Restrict Azure AI Services keys to specific IP ranges where possible
- Enable Azure Container Apps ingress restrictions for non-public deployments
- Review Bicep parameters before deploying to production