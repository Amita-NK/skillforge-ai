# Security Architecture & Best Practices

## Overview

SkillForge AI+ implements a **defense-in-depth** security strategy with multiple layers of protection. The Flask backend serves as the **central security gateway**, ensuring all requests are authenticated, validated, and authorized before accessing internal services.

## Security Principles

### 1. Zero Trust Architecture

**Principle**: Never trust, always verify.

- All requests must be authenticated
- All inputs must be validated
- All outputs must be sanitized
- Internal services are isolated from external access

### 2. Least Privilege

**Principle**: Grant minimum necessary permissions.

- Services run with minimal IAM permissions
- Database users have limited privileges
- API endpoints require specific JWT claims
- Network access is restricted by security groups

### 3. Defense in Depth

**Principle**: Multiple layers of security.

```
Layer 1: Network Security (Firewall, VPC, Security Groups)
Layer 2: Application Security (JWT, Input Validation)
Layer 3: Data Security (Encryption, Hashing)
Layer 4: Monitoring & Logging (CloudWatch, Audit Logs)
```

## Architecture Security

### Request Flow Security

```
┌─────────────┐
│  Frontend   │ ← HTTPS Only, CORS Configured
└──────┬──────┘
       │ JWT Token in Authorization Header
       ▼
┌─────────────┐
│   Backend   │ ← API Gateway (Security Checkpoint)
│  (Flask)    │   • JWT Validation
│             │   • Rate Limiting
│             │   • Input Validation
│             │   • SQL Injection Prevention
│             │   • XSS Protection
└──────┬──────┘
       │ Internal HTTP (Docker Network)
       ▼
┌─────────────┐
│ AI Service  │ ← Internal Only (Not Exposed)
│  (FastAPI)  │   • Input Validation
│             │   • Output Sanitization
└──────┬──────┘
       │ AWS SDK with IAM Roles
       ▼
┌─────────────┐
│   Bedrock   │ ← AWS Service (Encrypted)
└─────────────┘
```

### Critical Security Rule

**❌ NEVER expose AI Service directly to the internet**

```yaml
# ✅ CORRECT - AI Service is internal only
ai-service:
  expose:
    - "8000"  # Only accessible within Docker network
  # NO port mapping to host

# ❌ WRONG - DO NOT DO THIS
ai-service:
  ports:
    - "8000:8000"  # Exposes AI service to internet
```

**Why?**
- AI Service has no authentication
- Direct access bypasses rate limiting
- Exposes AWS credentials risk
- No audit logging
- No business logic enforcement

## Authentication & Authorization

### JWT Token Flow

```
1. User Login
   Frontend → POST /auth/login → Backend
                                    │
                                    ├─ Validate credentials
                                    ├─ Check password hash (bcrypt)
                                    ├─ Generate JWT token
                                    │
                                    └─ Return JWT

2. Authenticated Request
   Frontend → POST /ai/explain + JWT → Backend
                                          │
                                          ├─ Validate JWT signature
                                          ├─ Check expiration
                                          ├─ Extract user_id
                                          ├─ Verify permissions
                                          │
                                          └─ Process request
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "identity": "user_id",
    "exp": 1234567890,
    "iat": 1234567890
  },
  "signature": "..."
}
```

### Password Security

```python
# Registration
password_hash = generate_password_hash(password)  # bcrypt
user.password_hash = password_hash

# Login
if check_password_hash(user.password_hash, password):
    # Valid password
```

**Password Requirements** (Recommended):
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

## Input Validation

### Backend Validation

```python
# ✅ CORRECT - Validate all inputs
@app.route('/ai/quiz', methods=['POST'])
@jwt_required()
def generate_quiz():
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('topic'):
        return jsonify({'error': 'Topic is required'}), 400
    
    # Validate difficulty
    if data['difficulty'] not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400
    
    # Validate count range
    count = data.get('count', 5)
    if not isinstance(count, int) or count < 1 or count > 20:
        return jsonify({'error': 'Count must be between 1 and 20'}), 400
    
    # Sanitize topic (prevent injection)
    topic = str(data['topic']).strip()[:200]
```

### SQL Injection Prevention

```python
# ✅ CORRECT - Use SQLAlchemy ORM
user = User.query.filter_by(username=username).first()

# ✅ CORRECT - Use parameterized queries
user = User.query.filter(User.username == username).first()

# ❌ WRONG - Never use string concatenation
query = f"SELECT * FROM users WHERE username = '{username}'"  # VULNERABLE!
```

### XSS Prevention

```python
# ✅ CORRECT - Flask auto-escapes in templates
return render_template('page.html', user_input=user_input)

# ✅ CORRECT - Sanitize in JSON responses
from markupsafe import escape
return jsonify({'message': escape(user_input)})
```

## Network Security

### Docker Network Isolation

```yaml
networks:
  skillforge-network:
    driver: bridge
    # Internal network - services can communicate
    # External access only through exposed ports
```

**Network Rules:**
- Frontend: Exposed on port 3000 (development) or via CDN (production)
- Backend: Exposed on port 5000
- AI Service: **NOT exposed** (internal only)
- Database: **NOT exposed** (internal only)

### AWS Security Groups

```
┌─────────────────────────────────────────┐
│ Internet Gateway                         │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ Application Load Balancer                │
│ Security Group: Allow 443 from 0.0.0.0/0│
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ Backend ECS Service (Public Subnet)     │
│ Security Group: Allow 5000 from ALB     │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ AI Service ECS (Private Subnet)         │
│ Security Group: Allow 8000 from Backend │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ RDS Database (Private Subnet)           │
│ Security Group: Allow 3306 from Backend │
└─────────────────────────────────────────┘
```

## Data Security

### Encryption at Rest

- **Database**: RDS encryption enabled
- **OpenSearch**: Encryption at rest enabled
- **S3**: Server-side encryption (SSE-S3 or SSE-KMS)
- **Secrets**: AWS Secrets Manager with KMS encryption

### Encryption in Transit

- **Frontend ↔ Backend**: HTTPS (TLS 1.2+)
- **Backend ↔ AI Service**: HTTP (internal network, can use HTTPS)
- **Backend ↔ Database**: TLS connection
- **AI Service ↔ Bedrock**: HTTPS (AWS SDK)
- **AI Service ↔ OpenSearch**: HTTPS

### Secrets Management

```bash
# ✅ CORRECT - Use AWS Secrets Manager
aws secretsmanager create-secret \
  --name skillforge/backend/secrets \
  --secret-string '{
    "SECRET_KEY": "...",
    "JWT_SECRET_KEY": "...",
    "DATABASE_URL": "..."
  }'

# ✅ CORRECT - Use environment variables
SECRET_KEY = os.getenv('SECRET_KEY')

# ❌ WRONG - Never hardcode secrets
SECRET_KEY = "my-secret-key-123"  # VULNERABLE!
```

### Sensitive Data Handling

```python
# ✅ CORRECT - Never log sensitive data
logger.info(f"User {user_id} logged in")

# ❌ WRONG - Don't log passwords or tokens
logger.info(f"User logged in with password: {password}")  # VULNERABLE!
logger.info(f"JWT token: {token}")  # VULNERABLE!
```

## Rate Limiting

### Backend Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/ai/explain')
@limiter.limit("10 per minute")
@jwt_required()
def explain_concept():
    # Rate limited to 10 requests per minute per IP
    pass
```

### Bedrock Rate Limiting

```python
# Implement exponential backoff for Bedrock API
import time
from botocore.exceptions import ClientError

def invoke_bedrock_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = bedrock.invoke_model(...)
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                raise
```

## Monitoring & Auditing

### Audit Logging

```python
# Log all authentication attempts
logger.info(f"Login attempt: username={username}, ip={request.remote_addr}")

# Log all AI requests
logger.info(f"AI request: user={user_id}, endpoint={endpoint}, topic={topic}")

# Log all errors
logger.error(f"Error: {str(e)}, user={user_id}, endpoint={endpoint}")
```

### Security Monitoring

**Metrics to Monitor:**
- Failed login attempts (potential brute force)
- JWT validation failures (potential token tampering)
- Rate limit violations (potential abuse)
- Unusual API usage patterns
- Error rate spikes
- Unauthorized access attempts

**Alerts to Configure:**
- 5+ failed logins from same IP in 5 minutes
- 10+ JWT validation failures in 1 minute
- Error rate > 5% for 5 minutes
- Unusual traffic patterns

## CORS Configuration

```python
# ✅ CORRECT - Restrict CORS origins
CORS(app, origins=[
    "https://skillforge.com",
    "https://www.skillforge.com",
    "http://localhost:3000"  # Development only
])

# ❌ WRONG - Don't allow all origins in production
CORS(app, origins="*")  # VULNERABLE!
```

## Security Headers

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

## Vulnerability Prevention

### Common Vulnerabilities

| Vulnerability | Prevention |
|--------------|------------|
| SQL Injection | Use SQLAlchemy ORM, parameterized queries |
| XSS | Auto-escape templates, sanitize inputs |
| CSRF | Use CSRF tokens, SameSite cookies |
| Broken Authentication | Strong passwords, JWT with expiration |
| Sensitive Data Exposure | Encryption, secure secrets management |
| Broken Access Control | JWT validation, role-based access |
| Security Misconfiguration | Security headers, HTTPS only |
| Insecure Deserialization | Validate all inputs, use safe parsers |
| Using Components with Known Vulnerabilities | Regular dependency updates |
| Insufficient Logging | Comprehensive audit logging |

## Security Checklist

### Development

- [ ] Use environment variables for all secrets
- [ ] Never commit .env files
- [ ] Validate all user inputs
- [ ] Use parameterized queries
- [ ] Implement rate limiting
- [ ] Add comprehensive logging
- [ ] Use HTTPS in development (optional)

### Production

- [ ] Change all default passwords
- [ ] Use strong, unique secrets
- [ ] Enable HTTPS/TLS everywhere
- [ ] Configure security groups properly
- [ ] Enable encryption at rest
- [ ] Enable encryption in transit
- [ ] Set up AWS WAF
- [ ] Configure CloudTrail
- [ ] Set up security monitoring
- [ ] Implement backup strategy
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning
- [ ] Penetration testing

## Incident Response

### Security Incident Procedure

1. **Detect**: Monitor alerts and logs
2. **Contain**: Isolate affected systems
3. **Investigate**: Analyze logs and traces
4. **Remediate**: Fix vulnerability
5. **Recover**: Restore normal operations
6. **Review**: Post-incident analysis

### Emergency Contacts

- Security Team: security@skillforge.com
- AWS Support: [AWS Support Portal]
- On-Call Engineer: [PagerDuty/Slack]

## Compliance

### Data Protection

- **GDPR**: User data rights, consent, data portability
- **CCPA**: California privacy rights
- **SOC 2**: Security controls and auditing

### Best Practices

- Regular security training for developers
- Code review for security issues
- Automated security scanning (SAST/DAST)
- Regular penetration testing
- Bug bounty program (optional)

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

## Summary

**Key Security Principles:**

1. ✅ Backend is the **only** entry point for external requests
2. ✅ AI Service is **never** exposed to the internet
3. ✅ All requests are **authenticated** with JWT
4. ✅ All inputs are **validated** and **sanitized**
5. ✅ All secrets are **encrypted** and **managed** securely
6. ✅ All actions are **logged** for audit trail
7. ✅ All communications use **encryption** in transit
8. ✅ All data uses **encryption** at rest

**Remember**: Security is not a feature, it's a requirement. Every line of code should be written with security in mind.
