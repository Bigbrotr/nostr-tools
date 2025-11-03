# Security Policy

## 🔒 Security Commitment

The security of nostr-tools is our top priority. We are committed to protecting our users and their data by maintaining the highest security standards and promptly addressing any vulnerabilities.

## 📊 Supported Versions

We provide security updates for the following versions:

| Version | Supported          | Status              |
| ------- | ------------------ | ------------------- |
| 1.4.0   | ✅ Yes             | Active Support      |
| 1.3.0   | ❌ No              | End of Life         |
| 1.2.1   | ❌ No              | End of Life         |
| 1.2.0   | ❌ No              | End of Life         |
| 1.1.x   | ❌ No              | End of Life         |
| 1.0.x   | ❌ No              | End of Life         |
| < 1.0.0 | ❌ No              | End of Life         |

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
- **Timing Attack Protection**: Relies on secp256k1 library's constant-time implementations

### Input Validation

- **Event Validation**: All events are validated before processing (signatures, IDs, format)
- **URL Validation**: WebSocket URLs are strictly validated with regex patterns
- **Filter Validation**: Subscription filters are type-checked and validated
- **Null Character Prevention**: Events and tags are checked for null bytes

### Network Security

- **TLS/SSL Support**: Supports secure WebSocket connections (wss://) with fallback to ws://
- **Certificate Validation**: Relies on aiohttp's default SSL certificate validation
- **Timeout Protection**: Configurable connection and operation timeouts to prevent DoS
- **Automatic Reconnection**: Connection management with proper cleanup

### Dependency Security

- **Minimal Dependencies**: Only essential, well-maintained dependencies
- **Regular Updates**: Dependencies updated regularly
- **Security Scanning**: Automated scanning with Bandit, Safety and pip-audit
- **Version Pinning**: Explicit version requirements for reproducibility

## 🔍 Security Testing

### Automated Security Checks

Our CI/CD pipeline includes:

```bash
# Static analysis for security issues
bandit -r src/nostr_tools

# Dependency vulnerability scanning
safety scan --json || true
pip-audit --ignore-vuln GHSA-4xh5-x5gv-qwph --ignore-vuln PYSEC-2022-42991 --ignore-vuln GHSA-xqrq-4mgf-ff32 --skip-editable || true

# Comprehensive test suite
pytest --cov=nostr_tools --cov-fail-under=80
```

### Manual Security Review

Regular security reviews include:

- Code review for security issues
- Cryptographic implementation review
- Dependency audits and updates
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
from nostr_tools import Relay

relay = Relay("wss://relay.example.com")  # Secure TLS connection

# ⚠️  WARNING: The client will fallback to ws:// if wss:// fails
# For maximum security, verify relay URLs before use
relay = Relay("wss://verified-relay.example.com")

# ✅ GOOD: Validate relay configuration
try:
    relay = Relay(user_provided_url)
    relay.validate()  # Raises error if invalid
    if relay.is_valid:
        client = Client(relay)
except (TypeError, ValueError) as e:
    print(f"Invalid relay: {e}")
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
   - TLS/SSL support with fallback handling
   - Connection validation and timeout protection
   - Proper error handling and cleanup

4. **Application Layer**
   - Secure defaults
   - Principle of least privilege
   - Fail securely

### Threat Model

We aim to protect against:

- **Network Attacks**: TLS support to mitigate man-in-the-middle attacks
- **Injection Attacks**: Event validation to prevent malformed data
- **Cryptographic Attacks**: Signature verification and key validation
- **Information Disclosure**: No logging of private keys or sensitive data
- **Resource Issues**: Configurable timeouts to limit resource consumption

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
| 2025-11-02 | 1.3.0 | Updated supported versions - v1.3.0 only |
| 2025-10-05 | 1.2.1 | Updated supported versions - v1.2.1 only |
| 2025-10-04 | 1.2.0 | Initial security policy update |
| 2025-09-15 | 1.0.0 | Initial security policy |

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
