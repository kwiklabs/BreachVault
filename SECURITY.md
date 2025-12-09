# BreachVault Security Features

## Upload Security Validation

The chunked upload system includes comprehensive security checks to prevent malicious attacks:

### 1. **Malicious Pattern Detection**

Automatically blocks content containing:
- Script tags: `<script>`, `<?php>`, `<%>`
- SQL injection: `DROP TABLE`, `DELETE FROM`, `INSERT INTO`, `UNION SELECT`
- Code execution: `exec()`, `eval()`, `system()`, `shell_exec()`
- Template injection: `${...}`
- Path traversal: `../`
- Python imports: `__import__`

### 2. **File Format Validation**

- **UTF-8 Encoding**: Only valid UTF-8 text allowed
- **Line Length Limits**: Maximum 1000 characters per password
- **Character Validation**: Blocks excessive non-printable characters (>30%)
- **Null Byte Detection**: Prevents binary exploit attempts

### 3. **Content Sanitization**

Each password entry is sanitized:
- Control characters removed
- Whitespace trimmed
- Length limited to 1000 characters
- Comments stripped (`#`, `//`, `--`, `/*`)

### 4. **Smart Filtering**

Automatically skips:
- Comment lines
- Already-hashed entries (prevents hash re-hashing)
- Malformed entries
- Binary data

### 5. **Rate Limiting**

Built-in rate limiting (configured in middleware):
- 60 requests/minute per IP (default)
- Burst allowance: 10 requests
- Configurable in `config.yml`

### 6. **Session Management**

- 1-hour timeout for inactive sessions
- Automatic cleanup of expired sessions
- Upload ID validation with regex
- Protected against session hijacking

## Example Attack Scenarios Blocked

### ❌ SQL Injection Attempt
```
File content: password123'; DROP TABLE breached_hashes; --
Result: BLOCKED - Malicious pattern detected
```

### ❌ Script Injection
```
File content: <script>alert('xss')</script>
Result: BLOCKED - Script tag detected
```

### ❌ Code Execution
```
File content: password123\nsystem('rm -rf /')
Result: BLOCKED - Code execution pattern detected
```

### ❌ Binary Exploit
```
File content: [binary data with null bytes]
Result: BLOCKED - Null bytes detected
```

### ❌ Path Traversal
```
Filename: ../../../etc/passwd
Result: BLOCKED - Path traversal detected
```

### ✅ Valid Password List
```
File content:
password123
qwerty123
letmein
MySecureP@ssw0rd
```
Result: ACCEPTED - All entries processed

## Security Configuration

Edit `config.yml` to customize security settings:

```yaml
security:
  # Require authentication for admin panel
  require_admin_auth: true
  
  # Enable CORS
  cors_enabled: true
  cors_origins:
    - http://localhost:3000
    - https://yourdomain.com
  
  # JWT token expiration
  jwt_expiration_hours: 24

rate_limiting:
  enabled: true
  requests_per_minute: 60
  burst_size: 10
```

## Monitoring Suspicious Activity

Check logs for security events:

```bash
# View backend logs
./docker-manage.sh logs-backend

# Look for security warnings
docker compose logs backend | grep "Security validation failed"
docker compose logs backend | grep "Malicious pattern detected"
```

## Best Practices

1. **Always Use HTTPS in Production**
   - Configure SSL/TLS (see DEPLOYMENT_GUIDE.md)
   - Never run production on HTTP

2. **Change Default Credentials**
   ```bash
   # Edit .env file
   ADMIN_USERNAME=your_username
   ADMIN_PASSWORD=strong_password_here
   JWT_SECRET=$(openssl rand -hex 32)
   ```

3. **Restrict Admin Access**
   - Use IP whitelisting in nginx
   - Enable VPN-only access
   - Use strong passwords (16+ characters)

4. **Monitor Upload Patterns**
   - Set up alerts for failed uploads
   - Track suspicious IP addresses
   - Review logs regularly

5. **Keep Software Updated**
   ```bash
   ./docker-manage.sh update  # Pull latest code
   ```

6. **Database Backups**
   ```bash
   # Backup database
   docker compose exec postgres pg_dump -U breachvault breachvault > backup.sql
   
   # Restore database
   docker compose exec -T postgres psql -U breachvault breachvault < backup.sql
   ```

## Firewall Configuration

### UFW (Ubuntu)
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Block direct access to backend/database
# (use nginx reverse proxy instead)
```

### iptables
```bash
# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH, HTTP, HTTPS
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Drop everything else
iptables -A INPUT -j DROP
```

## Security Headers (Nginx)

```nginx
# Add security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

## Incident Response

If you detect a breach attempt:

1. **Immediately block the IP**
   ```bash
   sudo ufw deny from <attacker-ip>
   ```

2. **Review logs**
   ```bash
   ./docker-manage.sh logs-backend | grep <attacker-ip>
   ```

3. **Check for damage**
   ```bash
   ./docker-manage.sh db
   # Check for suspicious entries in database
   ```

4. **Rotate credentials**
   ```bash
   # Change admin password
   # Regenerate JWT secret
   # Restart services
   ./docker-manage.sh rebuild
   ```

## Security Checklist

- [ ] Changed default admin credentials
- [ ] Generated strong JWT_SECRET (32+ characters)
- [ ] Enabled HTTPS/TLS
- [ ] Configured firewall (UFW/iptables)
- [ ] Set up rate limiting
- [ ] Enabled security headers in nginx
- [ ] Restricted CORS origins
- [ ] Set up monitoring/alerts
- [ ] Configured automated backups
- [ ] Tested upload validation with malicious samples
- [ ] Documented incident response plan
- [ ] Regular security updates scheduled

## Reporting Security Issues

Found a security vulnerability? Please report it responsibly:

1. **DO NOT** open a public GitHub issue
2. Email: security@kwik.gg
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We'll respond within 48 hours and coordinate disclosure.
