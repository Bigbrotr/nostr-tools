# Security Policy

## Supported Versions

We actively support the following versions of nostr-tools with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of nostr-tools seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@bigbrotr.com**

Please include the following information in your report:

- Type of issue (buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### Response Timeline

- **Initial Response**: We will acknowledge receipt of your vulnerability report within 48 hours.
- **Investigation**: We will investigate and validate the vulnerability within 5 business days.
- **Resolution**: For confirmed vulnerabilities, we aim to release a fix within 2 weeks for critical issues, and within 4 weeks for moderate issues.
- **Disclosure**: We will coordinate with you on the timing of public disclosure.

### Vulnerability Disclosure Policy

- We will acknowledge your contribution in the security advisory (unless you prefer to remain anonymous)
- We will provide you with a timeline for when you can expect resolution
- We will notify you when the vulnerability is fixed
- We request that you keep vulnerability details confidential until we can release a fix

## Security Considerations

### Cryptographic Operations

This library handles sensitive cryptographic operations including:

- Private key generation and storage
- Event signing with Schnorr signatures
- Proof-of-work mining

**Important Security Notes:**

1. **Private Key Management**:
   - Never hardcode private keys in your application
   - Store private keys securely (encrypted at rest)
   - Use environment variables or secure key management systems
   - Consider using hardware security modules (HSMs) for production

2. **Random Number Generation**:
   - The library uses `os.urandom()` for secure random number generation
   - Ensure your system has sufficient entropy

3. **Network Communication**:
   - Always use WSS (WebSocket Secure) for relay connections when possible
   - Be cautious when using cleartext WS connections
   - Validate relay certificates

4. **Input Validation**:
   - The library validates all inputs, but always sanitize data from external sources
   - Be cautious with event content that may contain malicious data

### Tor Network Considerations

When using Tor relays:

- Ensure your SOCKS5 proxy is properly configured
- Be aware of potential timing correlation attacks
- Consider using Tor Browser's SOCKS proxy for better anonymity

### Dependencies

We regularly update dependencies to address security vulnerabilities:

- **secp256k1**: Cryptographic operations
- **aiohttp**: HTTP/WebSocket client
- **bech32**: Address encoding
- **aiohttp-socks**: SOCKS proxy support

Run `safety check` to scan for known vulnerabilities in dependencies.

## Best Practices for Developers

### Secure Development

1. **Code Review**: All code changes undergo security review
2. **Static Analysis**: We use tools like `bandit` for security scanning
3. **Dependency Scanning**: Regular scans with `safety` and `pip-audit`
4. **Testing**: Comprehensive test suite including security edge cases

### For Library Users

1. **Keep Updated**: Always use the latest version of nostr-tools
2. **Validate Inputs**: Sanitize and validate all external inputs
3. **Secure Storage**: Never store private keys in plaintext
4. **Network Security**: Use secure connections and validate certificates
5. **Error Handling**: Implement proper error handling to avoid information leakage

### Example Secure Usage

```python
import os
from nostr_tools import generate_keypair, Client, Relay

# Secure key generation
private_key, public_key = generate_keypair()

# Store keys securely (example - use proper key management in production)
os.environ['NOSTR_PRIVATE_KEY'] = private_key  # Better: use encrypted storage

# Use secure relay connections
relay = Relay("wss://relay.damus.io")  # WSS, not WS
client = Client(relay, timeout=30)

# Proper error handling
try:
    async with client:
        # Your code here
        pass
except Exception as e:
    # Log errors securely (don't expose sensitive data)
    print(f"Connection error occurred")  # Don't log the full exception
```

## Threat Model

### Assets Protected

- Private keys and cryptographic material
- Event content and metadata
- Network communications
- User privacy and anonymity

### Potential Threats

1. **Key Compromise**: Unauthorized access to private keys
2. **Network Attacks**: Man-in-the-middle, traffic analysis
3. **Code Injection**: Malicious content in events
4. **Denial of Service**: Resource exhaustion attacks
5. **Privacy Leaks**: Correlation of identities or activities

### Mitigations

- Secure key generation and storage
- Input validation and sanitization
- Rate limiting and resource management
- Secure network protocols
- Privacy-preserving practices

## Incident Response

In case of a security incident:

1. **Immediate Response**: Isolate affected systems
2. **Assessment**: Determine scope and impact
3. **Containment**: Prevent further damage
4. **Recovery**: Restore normal operations
5. **Lessons Learned**: Update security measures

## Contact

For security-related questions or concerns:

- **Security Email**: security@bigbrotr.com
- **General Contact**: hello@bigbrotr.com
- **GitHub Issues**: For non-security bugs only

## Acknowledgments

We appreciate the security research community's efforts to improve the security of nostr-tools and the broader Nostr ecosystem.
