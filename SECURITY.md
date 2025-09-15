# Security Policy

## 🔒 Security Commitment

The security of nostr-tools is our top priority. We are committed to protecting our users and their data by maintaining the highest security standards and promptly addressing any vulnerabilities.

## 📊 Supported Versions

We provide security updates for the following versions:

| Version | Supported          | Status              |
| ------- | ------------------ | ------------------- |
| 1.0.x   | ✅ Yes             | Active Support      |
| < 1.0   | ❌ No              | End of Life         |

## 🚨 Reporting a Vulnerability

### Do NOT Report Security Issues Publicly

Please **DO NOT** file public issues for security vulnerabilities. This helps protect users until a fix is available.

### How to Report

Report security vulnerabilities via email to:

**security@bigbrotr.com**

### What to Include

Please provide as much information as possible:

1. **Vulnerability Description**
   - Type of issue (e.g., buffer overflow, SQL injection, XSS)
   - Affected components
   - Security impact

2. **Reproduction Steps**
   - Detailed steps to reproduce the vulnerability
   - Proof-of-concept code (if applicable)
   - Environment details (OS, Python version, dependencies)

3. **Potential Impact**
   - Who could be affected
   - What data could be compromised
   - Severity assessment

4. **Suggested Fix** (optional)
   - If you have ideas for fixing the issue

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity (see below)

### Severity Levels and Response Times

| Severity | Description | Fix Timeline |
|----------|-------------|--------------|
| Critical | Remote code execution, authentication bypass, private key exposure | 24-48 hours |
| High | Data exposure, denial of service, cryptographic vulnerabilities | 3-7 days |
| Medium | Limited data exposure, requiring user interaction | 14-30 days |
| Low | Minor issues with minimal impact | 30-60 days |

## 🛡️ Security Measures

### Cryptographic Security

- **Key Generation**: Uses `os.urandom()` for cryptographically secure random numbers
- **Signing**: Implements secp256k1 using the proven `secp256k1` library
- **No Key Storage**: Private keys are never stored or logged by the library
- **Constant-Time Operations**: Cryptographic operations avoid timing attacks

### Input Validation

- **Event Validation**: All events are validated before processing
- **URL Validation**: WebSocket URLs are strictly validated
- **Filter Validation**: Subscription filters are sanitized
- **Size Limits**: Enforced limits on message and event sizes

### Network Security

- **TLS/SSL**: Enforces secure WebSocket connections (wss://)
- **Certificate Validation**: Proper SSL certificate validation
- **Timeout Protection**: Configurable timeouts to prevent DoS
- **Connection Limits**: Rate limiting and connection pooling

### Dependency Security

- **Minimal Dependencies**: Only essential, well-maintained dependencies
- **Regular Updates**: Dependencies updated regularly
- **Security Scanning**: Automated scanning with Safety and pip-audit
- **Version Pinning**: Explicit version requirements for reproducibility

## 🔍 Security Testing

### Automated Security Checks

Our CI/CD pipeline includes:

```bash
# Static analysis
bandit -r src/nostr_tools

# Dependency scanning
safety check
pip-audit

# Security-focused tests
pytest -m security
```

### Manual Security Review

Regular security reviews include:

- Code review for security issues
- Penetration testing of network components
- Cryptographic implementation review
- Third-party security audits (planned)

## 📋 Security Best Practices for Users

### Private Key Management

```python
# ✅ GOOD: Generate keys securely
from nostr_tools import generate_keypair
private_key, public_key = generate_keypair()

# ❌ BAD: Never hardcode private keys
private_key = "5340...secret...key"  # NEVER DO THIS!

# ✅ GOOD: Load from secure storage
import os
private_key = os.environ.get("NOSTR_PRIVATE_KEY")

# ✅ GOOD: Use key management service
from your_secure_storage import get_private_key
private_key = get_private_key()
```

### Connection Security

```python
# ✅ GOOD: Use secure WebSocket connections
relay = Relay("wss://relay.example.com")  # wss:// for TLS

# ❌ BAD: Avoid unencrypted connections
relay = Relay("ws://relay.example.com")  # Insecure!

# ✅ GOOD: Validate relay URLs
from nostr_tools import validate_relay_url
if validate_relay_url(url):
    relay = Relay(url)
```

### Error Handling

```python
# ✅ GOOD: Handle errors without exposing sensitive data
try:
    event.sign(private_key)
except Exception as e:
    logger.error("Failed to sign event")  # Don't log private_key!
    
# ❌ BAD: Never log sensitive information
logger.error(f"Failed with key: {private_key}")  # NEVER DO THIS!
```

## 🏗️ Security Architecture

### Defense in Depth

1. **Input Validation Layer**
   - Validate all external inputs
   - Sanitize user-provided data
   - Enforce strict typing

2. **Cryptographic Layer**
   - Secure key generation
   - Proper signature verification
   - No cryptographic material in logs

3. **Network Layer**
   - TLS/SSL enforcement
   - Connection validation
   - Rate limiting

4. **Application Layer**
   - Secure defaults
   - Principle of least privilege
   - Fail securely

### Threat Model

We protect against:

- **Network Attacks**: Man-in-the-middle, eavesdropping
- **Injection Attacks**: Event injection, filter manipulation
- **Cryptographic Attacks**: Key extraction, signature forgery
- **Denial of Service**: Resource exhaustion, connection flooding
- **Information Disclosure**: Key leakage, metadata exposure

## 🔄 Security Updates

### Staying Informed

- **Security Advisories**: Published on [GitHub Security](https://github.com/bigbrotr/nostr-tools/security/advisories)
- **Release Notes**: Security fixes noted in [CHANGELOG.md](CHANGELOG.md)
- **Email Notifications**: Subscribe to security announcements

### Updating

```bash
# Check current version
pip show nostr-tools

# Update to latest version
pip install --upgrade nostr-tools

# Verify update
python -c "import nostr_tools; print(nostr_tools.__version__)"
```

## 🤝 Responsible Disclosure

We follow responsible disclosure practices:

1. **Private Disclosure**: Security issues reported privately
2. **Fix Development**: Develop and test fixes
3. **Coordinated Release**: Release fix with security advisory
4. **Public Disclosure**: Details published after fix is available
5. **Credit**: Security researchers credited (unless they prefer anonymity)

## 📜 Security Policy History

| Date | Version | Changes |
|------|---------|---------|
| 2024-12-20 | 1.0.0 | Initial security policy |

## 🙏 Acknowledgments

We thank the following security researchers for responsibly disclosing vulnerabilities:

- *Your name could be here!*

## 📞 Contact

- **Security Issues**: security@bigbrotr.com
- **General Inquiries**: hello@bigbrotr.com
- **PGP Key**: Available on request for encrypted communication

---

**Remember**: Security is everyone's responsibility. If you see something, say something!

Thank you for helping keep nostr-tools secure! 🔐