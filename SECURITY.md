# Security Policy

## Supported Versions

We actively support security updates for the following versions of the Barsic Bot:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The Barsic Bot team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:
- **Primary Contact**: [bazhenov.in@gmail.com](mailto:bazhenov.in@gmail.com)
- **Subject**: `[SECURITY] Barsic Bot Vulnerability Report`

### What to Include

When reporting a vulnerability, please include the following information:
- **Description**: A clear description of the vulnerability
- **Impact**: The potential impact and severity of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the vulnerability
- **Proof of Concept**: If applicable, include a proof of concept
- **Suggested Fix**: If you have suggestions for how to fix the issue
- **Environment**: Version information and environment details

### Response Timeline

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Status Updates**: We will keep you informed of our progress throughout the investigation
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

### Security Best Practices

When using the Barsic Bot, we recommend following these security best practices:

#### Bot Token Security
- Never commit bot tokens to version control
- Use environment variables or secure configuration files for tokens
- Regularly rotate bot tokens if compromised
- Monitor bot usage for suspicious activity

#### Configuration Security
- Use strong, unique secrets for API keys
- Enable debug mode only in development environments
- Use environment-specific configuration files
- Regularly update configuration templates

#### Redis Security
- Use Redis authentication if available
- Configure Redis to bind to specific interfaces only
- Monitor Redis access logs
- Use Redis ACLs for fine-grained access control

#### Role-Based Access
- Regularly review admin user permissions
- Monitor for unauthorized privilege escalation
- Implement proper user verification processes
- Log all administrative actions

#### API Integration Security
- Use HTTPS for all external API communications
- Validate all API responses before processing
- Implement proper timeout handling
- Monitor API usage for abuse patterns

#### Infrastructure Security
- Keep Docker images updated
- Use non-root users in containers
- Enable container security scanning
- Implement proper network segmentation

### Known Security Considerations

- **Bot Tokens**: Telegram bot tokens provide full access to bot functionality
- **Role Management**: Admin roles have elevated privileges in the system
- **Redis Storage**: User state and session data stored in Redis
- **API Communications**: External API calls may contain sensitive data
- **User Blocking**: Middleware can block users but logs should be monitored

### Security Features

The Barsic Bot includes several built-in security features:
- **Role-Based Access Control**: Separate admin and user permissions
- **Private Chat Only**: Bot only operates in private chats
- **User Blocking Middleware**: Ability to block unauthorized users
- **Permission Filters**: Comprehensive permission checking system
- **Input Validation**: Pydantic-based validation for all inputs
- **Error Handling**: Secure error responses without information leakage
- **State Management**: Secure Redis-based state persistence

### Bot-Specific Security

#### Telegram Security
- Bot operates only in private chats to prevent information leakage
- Implements proper error handling to avoid exposing sensitive information
- Uses webhook deletion to prevent message buildup
- Implements proper bot token management

#### Dialog System Security
- State isolation between different users
- Secure dialog state transitions
- Input validation at dialog level
- Protection against dialog manipulation

#### Middleware Security
- Blocked user detection and prevention
- Chat type validation
- Permission verification before handler execution
- Comprehensive logging of security events

### Responsible Disclosure

We follow responsible disclosure practices:
- We will work with you to understand and resolve the issue
- We will not take legal action against researchers who follow this policy
- We will credit researchers who report valid vulnerabilities (unless they prefer to remain anonymous)
- We may publish security advisories after issues are resolved

### Bug Bounty

Currently, we do not have a formal bug bounty program, but we greatly appreciate security researchers who help us improve the security of our bot service.

## Contact

For non-security related issues, please use GitHub issues or contact the maintainer through standard channels.

For urgent security matters outside of vulnerability reports, you can also reach out via:
- GitHub: [@sendhello](https://github.com/sendhello)
- Email: [bazhenov.in@gmail.com](mailto:bazhenov.in@gmail.com)

---

*Last updated: August 2025*