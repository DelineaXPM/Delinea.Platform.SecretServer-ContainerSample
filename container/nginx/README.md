# NGINX Proxy - TLS Termination

## Overview

NGINX reverse proxy that provides HTTPS/TLS termination for the Delinea Sidecar API.

```
Client (HTTPS:8443) → NGINX Proxy (TLS) → Sidecar (HTTP:8080)
```

---

## SSL Certificate Setup

### For Testing/Development

We provide scripts to quickly generate self-signed certificates for testing:

**Linux/macOS/WSL:**
```bash
chmod +x setup_ssl_linux.sh
./setup_ssl_linux.sh
```

**Windows (Git Bash):**
```bash
bash setup_ssl_windows.sh
```

This creates certificates in the `nginx/ssl/` folder:
- `server.key` - Your private key
- `server.crt` - Your certificate

**⚠️ Important:** These are self-signed certificates meant only for testing. Your browser will show security warnings, which is expected.

### For Production

**⚠️ Don't use self-signed certificates in production.** Get proper certificates from a trusted Certificate Authority (like Let's Encrypt, DigiCert, etc.) and place them in `nginx/ssl/` before deploying.

---

## Starting NGINX

```bash
docker compose up -d nginx-proxy
```

---

## Testing

```bash
# Test the health endpoint
curl -k https://localhost:8443/health

# The -k flag ignores certificate warnings (only use for testing!)
```

---

## Configuration

The `nginx.conf` file provides:
- HTTPS on port 8443
- HTTP to HTTPS redirect on port 8080
- Security headers
- Rate limiting
- Connection to the sidecar backend

---

## Troubleshooting

**"Certificate not found" error:**
```bash
# Make sure certificates exist
ls nginx/ssl/

# If missing, regenerate them
./setup_ssl_linux.sh
docker compose restart nginx-proxy
```

**Can't connect to NGINX:**
```bash
# Check if it's running
docker compose ps nginx-proxy

# View logs
docker compose logs nginx-proxy
```

**502 Bad Gateway:**
```bash
# Check if sidecar is running
docker compose ps sidecar
```

---

## Renewing Certificates

Self-signed certificates expire after 1 year. To renew:

```bash
rm -rf nginx/ssl/*
./setup_ssl_linux.sh
docker compose restart nginx-proxy
```

For production certificates, follow your CA's renewal process.

---

## Quick Commands

```bash
# Generate certificates
./setup_ssl_linux.sh

# Start
docker compose up -d nginx-proxy

# View logs
docker compose logs -f nginx-proxy

# Restart
docker compose restart nginx-proxy

# Stop
docker compose stop nginx-proxy
```