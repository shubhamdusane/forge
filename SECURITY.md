# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within **Forge**, please send an email to sdusane4@gmail.com. All reports will be promptly addressed.

**Please include the following in your report:**

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if applicable)
- Your contact information for follow-up

## Response Timeline

- **Acknowledgment:** Within 48 hours of report submission
- **Initial Assessment:** Within 72 hours
- **Fix Deployment:** Within 7 days for confirmed vulnerabilities

## Security Update Process

1. Vulnerability reports are triaged and prioritized
2. A fix is developed and tested in a private branch
3. Security patch is released as a minor or patch version bump
4. Affected users are notified via release notes
5. CVE is requested if applicable

## Security-Related Configuration

- All API endpoints require authentication via JWT tokens
- Rate limiting is enforced on public endpoints
- CORS policies restrict cross-origin access to trusted domains
- Environment variables must never be committed to version control
- Secrets are managed through a dedicated secrets manager

## Known Security Gaps

- File upload validation relies on extension checks; content-type sniffing is not fully mitigated
- WebSocket connections do not currently enforce TLS verification on internal networks
- Audit logging is limited to authentication events only
