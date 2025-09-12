# Security Policy

## Overview

Security is fundamental to nostr-tools, as the library handles sensitive cryptographic operations and network communications in the Nostr protocol ecosystem. This document outlines our security policies, reporting procedures, and best practices for developers and users.

## 📋 Supported Versions

We provide security updates for the following versions of nostr-tools:

| Version | Security Support | Support Status | End of Life |
|---------|------------------|----------------|-------------|
| 0.1.x   | ✅ **Active**   | Full support  | TBD         |
| < 0.1.0 | ❌ **Deprecated** | None         | Immediate   |

### Security Update Policy

- **Critical vulnerabilities**: Patch released within 48 hours
- **High severity**: Patch released within 1 week  
- **Medium severity**: Patch released within 2 weeks
- **Low severity**: Included in next scheduled release

## 🚨 Reporting Security Vulnerabilities

**Please DO NOT report security vulnerabilities through public GitHub issues.**

### Reporting Process

1. **Email**: Send detailed vulnerability reports to **security@bigbrotr.com**
2. **Response Time**: We will acknowledge receipt within 48 hours
3. **Confidentiality**: Please keep vulnerability details confidential until we release a fix

### Information to Include

Please provide as much detail as possible:

- **Vulnerability Type**: Buffer overflow, injection, authentication bypass, etc.
- **Affected Components**: Specific modules, functions, or classes
- **Impact Assessment**: Potential consequences if exploited
- **Attack Scenario**: Step-by-step reproduction instructions
- **Proof of Concept**: Code demonstrating the vulnerability (if safe to share)
- **Affected Versions**: Which versions are vulnerable
- **Suggested Fix**: If you have ideas for remediation
- **Discovery Context**: How you discovered the vulnerability
- **Credit Information**: How you'd like to be credited (or remain anonymous)

### Vulnerability Report Template

```
Subject: [SECURITY] Vulnerability Report - [Brief Description]

Vulnerability Details:
- Type: [e.g., Cryptographic weakness, Input validation, etc.]
- Severity: [Critical/High/Medium/Low - your assessment]
- Component: [e.g., nostr_tools.core.event, utils.crypto, etc.]
- Versions Affected: [e.g., 0.1.0 and later]

Description:
[Detailed description of the vulnerability]

Impact:
[Potential security impact if exploited]

Reproduction Steps:
1. [Step one]
2. [Step two]
3. [Result/Impact]

Proof of Concept:
[Code or commands demonstrating the issue - if safe to share]

Suggested Mitigation:
[Your suggestions for fixing the vulnerability]

Additional Information:
[Any other relevant details]

Credit:
[How you'd like to be acknowledged, or "Anonymous" if preferred]
```

## 🔒 Security Architecture

### Cryptographic Security

nostr-tools implements industry-standard cryptographic practices:

#### **Elliptic Curve Cryptography**
- **Library**: `secp256k1` (Bitcoin's elliptic curve)
- **Key Generation**: Secure random number generation using `os.urandom()`
- **Signature Scheme**: Schnorr signatures as specified in NIP-01
- **Key Validation**: Comprehensive validation of all cryptographic inputs

#### **Random Number Generation**
```python
# Secure entropy source
import os
private_key_bytes = os.urandom(32)  # 256 bits of entropy
```

#### **Memory Safety**
- Automatic cleanup of sensitive data structures
- No persistence of private keys in memory longer than necessary
- Protection against memory dumps containing sensitive data

### Network Security

#### **Transport Layer Security**
- **Default Protocol**: WSS (WebSocket Secure) preferred over WS
- **TLS Validation**: Proper certificate validation for secure connections
- **Tor Support**: Native .onion relay support with SOCKS5 proxy

#### **Connection Security**
```python
# ✅ Secure connection (recommended)
relay = Relay("wss://relay.example.com")

# ⚠️ Insecure connection (avoid in production)
relay = Relay("ws://relay.example.com")
```

### Input Validation Security

#### **Comprehensive Validation**
- All inputs validated for type, format, and range
- Protection against null-byte injection attacks
- Validation of event structure according to NIP-01
- Sanitization of untrusted data from network sources

#### **Example Validation**
```python
def validate_event_data(data: Dict[str, Any]) -> None:
    """Comprehensive event validation with security checks."""
    # Type validation
    if not isinstance(data, dict):
        raise TypeError("Event data must be a dictionary")

    # Required field validation
    required_fields = ["id", "pubkey", "created_at", "kind", "tags", "content", "sig"]
    for field in required_fields:
        if field not in data:
            raise KeyError(f"Missing required field: {field}")

    # Format validation
    if not re.match(r"^[0-9a-f]{64}$", data["id"]):
        raise ValueError("Invalid event ID format")

    # Content sanitization
    if "\x00" in data["content"]:
        raise ValueError("Null bytes not allowed in content")
```

## 🛡️ Security Best Practices

### For Library Users

#### **Private Key Management**
```python
import os
from nostr_tools import generate_keypair

# ✅ DO: Use environment variables for key storage
private_key = os.getenv('NOSTR_PRIVATE_KEY')
if not private_key:
    private_key, public_key = generate_keypair()
    # Store securely (use proper key management in production)

# ✅ DO: Use secure key generation
private_key, public_key = generate_keypair()  # Uses os.urandom()

# ❌ DON'T: Hardcode private keys
# private_key = "..."  # Never do this!

# ❌ DON'T: Store keys in plaintext files
# with open('private_key.txt', 'w') as f:
#     f.write(private_key)  # Insecure!
```

#### **Network Security**
```python
from nostr_tools import Relay, Client

# ✅ DO: Use secure WebSocket connections
relay = Relay("wss://relay.example.com")  # Encrypted connection

# ✅ DO: Validate relay certificates (automatic)
client = Client(relay, timeout=30)

# ✅ DO: Use Tor for enhanced privacy when needed
tor_relay = Relay("wss://example.onion")
tor_client = Client(
    tor_relay,
    socks5_proxy_url="socks5://127.0.0.1:9050"
)

# ⚠️ AVOID: Unencrypted connections in production
# relay = Relay("ws://relay.example.com")  # Unencrypted!
```

#### **Input Validation**
```python
from nostr_tools import Event, sanitize

# ✅ DO: Validate all external data
def safe_event_handler(event_data):
    try:
        # Automatic validation during Event creation
        event = Event.from_dict(event_data)

        # Additional sanitization for display
        safe_content = sanitize(event.content)
        return safe_content
    except (ValueError, TypeError) as e:
        print(f"Invalid event rejected: {e}")
        return None

# ✅ DO: Sanitize data from untrusted sources
untrusted_data = {"content": "Hello\x00World"}
clean_data = sanitize(untrusted_data)  # Removes null bytes
```

#### **Error Handling**
```python
from nostr_tools import RelayConnectionError
import logging

# ✅ DO: Handle errors gracefully without information leakage
async def secure_relay_connection():
    try:
        async with client:
            # Relay operations
            pass
    except RelayConnectionError as e:
        # Log error securely (don't expose sensitive info)
        logging.warning("Relay connection failed")
        # Don't log the full exception in production
    except Exception as e:
        # Catch unexpected errors
        logging.error("Unexpected error occurred")
        # Don't expose internal details to users

# ❌ DON'T: Expose sensitive information in error messages
# except Exception as e:
#     print(f"Error: {e}")  # May contain sensitive details
```

### For Library Contributors

#### **Secure Development Practices**
```python
# ✅ DO: Validate all inputs comprehensively
def process_relay_metadata(data: Any) -> Optional[Dict[str, Any]]:
    # Type validation
    if not isinstance(data, dict):
        return None

    # Sanitize all string values
    sanitized = {}
    for key, value in data.items():
        if isinstance(key, str) and isinstance(value, (str, int, list, dict)):
            sanitized[sanitize(key)] = sanitize(value)

    return sanitized

# ✅ DO: Use type hints for security clarity
def sign_event(private_key: str, event_id: str) -> str:
    """Sign event with proper type validation."""
    if not isinstance(private_key, str) or len(private_key) != 64:
        raise ValueError("Invalid private key format")
    # Implementation...

# ✅ DO: Implement comprehensive error handling
def validate_signature(event_id: str, pubkey: str, signature: str) -> bool:
    """Validate signature with proper error handling."""
    try:
        # Validation logic
        return True
    except Exception:
        # Never expose internal cryptographic errors
        return False
```

#### **Testing Security**
```python
# Security-focused test example
@pytest.mark.security
def test_private_key_not_exposed_in_error():
    """Ensure private keys are not exposed in error messages."""
    private_key = "..."

    try:
        # Trigger an error condition
        result = some_operation(private_key)
    except Exception as e:
        error_message = str(e)

        # Verify sensitive data is not in error message
        assert private_key not in error_message
        assert "sensitive" not in error_message.lower()
```

## 🔍 Security Testing and Auditing

### Automated Security Testing

We use multiple layers of automated security testing:

#### **Static Security Analysis**
```bash
# Bandit - Security vulnerability scanner
bandit -r nostr_tools -f json

# Safety - Dependency vulnerability scanner  
safety check --json

# Semgrep - Static analysis security scanner
semgrep --config=p/security-audit nostr_tools/
```

#### **Dependency Security**
```bash
# Check for known vulnerabilities in dependencies
pip-audit --format=json --output=security-report.json

# Regular dependency updates
pip list --outdated
```

### Manual Security Review Checklist

#### **Code Review Security Checklist**
- [ ] **Input Validation**: All inputs validated and sanitized
- [ ] **Cryptographic Operations**: Proper use of cryptographic libraries
- [ ] **Error Handling**: No sensitive data leaked in error messages
- [ ] **Memory Management**: Sensitive data properly cleaned up
- [ ] **Network Security**: Secure connections used by default
- [ ] **Authentication**: Proper authentication mechanisms
- [ ] **Authorization**: Appropriate access controls
- [ ] **Logging**: No sensitive data logged

#### **Cryptographic Review**
- [ ] **Random Number Generation**: Uses cryptographically secure randomness
- [ ] **Key Management**: Proper key generation, storage, and disposal
- [ ] **Signature Validation**: Comprehensive signature verification
- [ ] **Hash Functions**: Appropriate hash functions for use case
- [ ] **Timing Attacks**: Protection against timing-based attacks

## 🚨 Incident Response

### Security Incident Classification

#### **Critical (P0)**
- Remote code execution vulnerabilities
- Private key extraction or compromise
- Authentication bypass allowing unauthorized access
- Mass data exposure or privacy breaches

#### **High (P1)**  
- Local privilege escalation
- Signature verification bypass
- Denial of service affecting availability
- Information disclosure of sensitive data

#### **Medium (P2)**
- Input validation issues
- Minor information disclosure
- Performance degradation attacks
- Configuration security issues

#### **Low (P3)**
- Security improvements
- Hardening opportunities
- Documentation security issues

### Response Timeline

| Severity | Acknowledgment | Initial Assessment | Patch Development | Patch Release |
|----------|---------------|-------------------|-------------------|---------------|
| Critical | 2 hours       | 4 hours           | 24 hours          | 48 hours      |
| High     | 8 hours       | 1 day             | 3 days            | 1 week        |
| Medium   | 1 day         | 3 days            | 1 week            | 2 weeks       |
| Low      | 3 days        | 1 week            | Next release      | Next release  |

### Incident Response Process

1. **Initial Response**
   - Acknowledge vulnerability report
   - Assign severity level
   - Form response team
   - Begin impact assessment

2. **Investigation**
   - Reproduce the vulnerability
   - Assess scope and impact
   - Identify affected versions
   - Develop mitigation strategy

3. **Fix Development**
   - Develop security patch
   - Test fix comprehensively
   - Prepare security advisory
   - Coordinate disclosure timeline

4. **Disclosure and Release**
   - Release security update
   - Publish security advisory
   - Notify users and downstream projects
   - Credit security researcher

5. **Post-Incident**
   - Conduct security review
   - Improve security measures
   - Update documentation
   - Share lessons learned

## 🛠️ Security Tools and Resources

### Development Security Tools

#### **Required Tools**
- **Bandit**: Security issue identification in Python code
- **Safety**: Known security vulnerabilities in dependencies  
- **MyPy**: Static type checking to prevent type-related vulnerabilities
- **Ruff**: Modern linter with security-focused rules

#### **Recommended Tools**
- **Semgrep**: Advanced static analysis for security patterns
- **pip-audit**: Comprehensive dependency vulnerability scanning
- **Detect-secrets**: Prevent accidental commit of secrets
- **Pre-commit**: Automated security checks before commits

#### **Security Testing Commands**
```bash
# Run comprehensive security scan
make security-scan

# Check dependencies for vulnerabilities  
make deps-check

# Run security-focused tests
make test-security

# Full security validation
bandit -r nostr_tools && safety check && pytest -m security
```

### Security Resources

#### **Nostr Protocol Security**
- [NIP-01 Specification](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [Nostr Security Considerations](https://github.com/nostr-protocol/nips)
- [Schnorr Signature Security](https://bip340.org/)

#### **Cryptographic Resources**
- [secp256k1 Documentation](https://github.com/bitcoin-core/secp256k1)
- [Python Cryptography Best Practices](https://cryptography.io/)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)

#### **Python Security**
- [Python Security Documentation](https://docs.python.org/3/library/security.html)
- [OWASP Python Security](https://owasp.org/www-project-python-security/)
- [Bandit Security Linter](https://bandit.readthedocs.io/)

## 📚 Security Education

### Common Security Pitfalls

#### **Cryptographic Mistakes**
```python
# ❌ DON'T: Use weak random number generation
import random
weak_key = random.randint(1, 2**256)  # Predictable!

# ✅ DO: Use cryptographically secure random generation
import os
secure_key = os.urandom(32)  # Cryptographically secure
```

#### **Key Management Errors**
```python
# ❌ DON'T: Log private keys
logging.info(f"Generated key: {private_key}")  # Sensitive data!

# ✅ DO: Log only non-sensitive information
logging.info("Keypair generated successfully")
```

#### **Input Validation Bypass**
```python
# ❌ DON'T: Trust external data
def process_event(data):
    event_id = data["id"]  # What if data is not a dict?
    # Process without validation...

# ✅ DO: Validate everything
def process_event(data):
    if not isinstance(data, dict):
        raise TypeError("Expected dictionary")

    event = Event.from_dict(data)  # Comprehensive validation
    # Safe to process validated event
```

### Security Training Resources

1. **Cryptography Fundamentals**
   - Understanding elliptic curve cryptography
   - Schnorr signature security properties
   - Key generation and management best practices

2. **Network Security**
   - TLS/SSL certificate validation
   - WebSocket security considerations
   - Tor network privacy implications

3. **Input Validation**
   - Sanitization techniques
   - Injection attack prevention
   - Data structure validation

4. **Secure Development**
   - Threat modeling
   - Security code review practices
   - Vulnerability assessment techniques

## 🤝 Security Community

### Responsible Disclosure

We support and encourage responsible disclosure of security vulnerabilities. Security researchers who follow our responsible disclosure process will receive:

- **Recognition**: Public acknowledgment in security advisories (if desired)
- **Response**: Timely communication throughout the process
- **Collaboration**: Working together to understand and fix issues
- **Credit**: Appropriate credit for discovering and reporting issues

### Security Hall of Fame

We maintain a security hall of fame to recognize researchers who have helped improve nostr-tools security:

*[No security reports received yet - be the first!]*

### Community Security Guidelines

1. **Report Responsibly**: Follow our disclosure process
2. **Test Safely**: Don't test vulnerabilities on production systems
3. **Respect Privacy**: Don't access or modify data you don't own
4. **Be Patient**: Allow time for proper fixes before public disclosure
5. **Be Collaborative**: Work with us to understand and resolve issues

## 📞 Contact Information

### Security Team
- **Email**: security@bigbrotr.com
- **Response Time**: Within 48 hours
- **Languages**: English

### General Security Questions
- **Email**: hello@bigbrotr.com
- **Discussion**: [GitHub Discussions](https://github.com/bigbrotr/nostr-tools/discussions)

### Emergency Contact
For critical security issues requiring immediate attention:
- **Email**: security@bigbrotr.com (mark as URGENT in subject)
- **Response**: Within 2 hours during business hours

---

## 📋 Security Policy Updates

This security policy is reviewed and updated regularly to reflect:
- Changes in the threat landscape
- New security features and improvements
- Lessons learned from security incidents
- Community feedback and best practices

**Last Updated**: January 12, 2025
**Next Review**: July 12, 2025

---

**Remember**: Security is everyone's responsibility. If you see something suspicious or have security concerns, please don't hesitate to reach out. Together, we can build a more secure Nostr ecosystem.
