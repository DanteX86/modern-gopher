# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in Modern Gopher, please report it responsibly.

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please email us directly at: [security@modern-gopher.dev](mailto:security@modern-gopher.dev)

Include the following information:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested fixes (if known)

### What to Expect

1. **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
2. **Investigation**: We will investigate the issue and determine its validity and severity
3. **Updates**: We will provide regular updates on our progress
4. **Resolution**: We will work on a fix and coordinate disclosure timing with you
5. **Credit**: We will credit you in our security advisories (unless you prefer to remain anonymous)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 1 week
- **Fix Development**: Depends on severity and complexity
- **Disclosure**: Coordinated with reporter

## Security Considerations

### Network Security

Modern Gopher connects to external Gopher servers, which involves:
- **SSL/TLS Support**: Use `gophers://` URLs for encrypted connections
- **Connection Validation**: Verify server certificates when using SSL
- **Timeout Handling**: Prevent hanging connections with configurable timeouts

### Input Validation

- **URL Parsing**: All Gopher URLs are validated before processing
- **Content Filtering**: User input is sanitized to prevent injection attacks
- **File Path Validation**: Local file operations use secure path handling

### Data Privacy

- **Local Storage**: Configuration and cache files are stored with appropriate permissions
- **Session Data**: Browser sessions contain only navigation history and preferences
- **No Telemetry**: No usage data is collected or transmitted

### Configuration Security

- **File Permissions**: Configuration files use restrictive permissions (600)
- **Input Validation**: All configuration values are validated
- **Safe Defaults**: Secure default settings are used

## Best Practices for Users

### Secure Usage

1. **Use SSL/TLS**: Prefer `gophers://` URLs when available
2. **Verify Content**: Be cautious when opening untrusted content
3. **Regular Updates**: Keep Modern Gopher updated to the latest version
4. **Configuration Review**: Regularly review your configuration for security

### Network Environment

1. **Firewall**: Use appropriate firewall rules
2. **Proxy Support**: Use proxies in restricted environments
3. **DNS Security**: Use secure DNS providers

## Security Features

### Current Protections

- **SSL/TLS Support**: Encrypted connections to supporting servers
- **Input Validation**: All user input is validated and sanitized
- **Safe File Handling**: Secure local file operations
- **Connection Timeouts**: Prevent resource exhaustion
- **Error Handling**: Graceful handling of network errors

### Planned Security Enhancements

- **Certificate Pinning**: Enhanced SSL certificate validation
- **Content Security**: Advanced content filtering options
- **Audit Logging**: Optional security event logging
- **Sandboxing**: Plugin execution sandboxing

## Dependencies

We regularly monitor our dependencies for security vulnerabilities:

- **Automated Scanning**: GitHub Dependabot alerts
- **Manual Review**: Regular dependency audits
- **Timely Updates**: Prompt updates for security fixes

## Secure Development

### Our Practices

- **Security Reviews**: Code reviews include security considerations
- **Static Analysis**: Automated security scanning with Bandit
- **Dependency Scanning**: Regular dependency vulnerability checks
- **Secure Coding**: Following secure coding best practices

### Testing

- **Security Tests**: Dedicated security-focused test cases
- **Penetration Testing**: Regular security assessments
- **Fuzzing**: Input validation testing

## Disclosure Policy

### Coordinated Disclosure

We follow responsible disclosure practices:
1. Security issues are fixed before public disclosure
2. Reporters are given time to verify fixes
3. Public disclosure includes mitigation strategies
4. Credit is given to security researchers

### Security Advisories

We publish security advisories for significant vulnerabilities:
- **GitHub Security Advisories**: Primary disclosure channel
- **CHANGELOG**: Security fixes are noted in release notes
- **Documentation**: Security guidance is updated as needed

## Contact Information

- **Security Email**: [security@modern-gopher.dev](mailto:security@modern-gopher.dev)
- **General Issues**: [GitHub Issues](https://github.com/DanteX86/modern-gopher/issues)
- **Discussions**: [GitHub Discussions](https://github.com/DanteX86/modern-gopher/discussions)

---

Thank you for helping keep Modern Gopher secure! 🔐

