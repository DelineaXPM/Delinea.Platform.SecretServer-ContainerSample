# 🧩 Delinea Platform Secret-Server Sidecar — Quick Start

This small **sidecar service** connects to **Delinea Secret Server or Platform**, fetches secrets at regular intervals, and exposes them through a lightweight **HTTP API**.

> For development, it can also run behind an `nginx-proxy` that provides HTTPS (TLS) termination.

---

## 📘 Overview

The sidecar:
- Connects to Delinea Secret Server/Platform
- Fetches configured secrets periodically
- Exposes them via these HTTP endpoints:

| Endpoint | Description |
|-----------|--------------|
| **GET /health** | Returns service status and cache info |
| **GET /secrets** | Lists available secret names |
| **GET /secrets/<name>** | Returns full secret fields for the given secret |

---

## 🚀 Quick Start (Local)

1. **Set up Python**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -U pip
   pip install -r requirements.txt
   ```

2. **Provide Secret-Server/Platform credentials**

   Create a file (default path: `/run/secrets/server_creds`) with the following:
   ```
   SERVER_URL=https://your-secret-server-or-platform
   SERVER_USERNAME=example
   SERVER_PASSWORD=secret
   ```

   For local runs, you can edit this file manually or adjust `src/delinea_secrets/secret_manager.py`.

3. **Specify which secrets to fetch**

   - Using JSON (recommended):
     ```powershell
     $env:SECRETS_CONFIG = '[{"id":11126,"name":"mongo-secret","fields":"database,username,password"}]'
     ```

   - Or a simple list:
     ```powershell
     $env:SECRETS_CONFIG = '11126,11113'
     ```

4. **Run the sidecar**
   ```powershell
   python -m src.main
   ```

---

## 🐳 Quick Start (Docker Compose)

Run both the sidecar and HTTPS proxy:
```powershell
docker-compose up --build sidecar nginx-proxy
```

**Notes:**
- `nginx-proxy` handles HTTPS on port **8443** and forwards to the sidecar on port **8080**
- Dev TLS certs live in `nginx/ssl` — do **not** use them in production
- Access locally via: `https://localhost:8443`

---

## ⚙️ Configuration

| Variable | Description | Default |
|-----------|--------------|----------|
| `SECRETS_CONFIG` | Secrets to fetch (JSON or IDs) | **Required** |
| `POLL_INTERVAL` | Poll frequency (seconds) | `60` |
| `HTTP_PORT` | Sidecar port | `8080` |
| `BIND_HOST` | Bind address | `127.0.0.1` (local), `0.0.0.0` (Docker) |

---

## 🔐 Certificates (for Docker Compose)

- Dev certs: `nginx/ssl/server.crt` and `server.key`
- Proxy provides HTTPS on **8443**
- Internal containers may need to trust the cert using:
  ```bash
  update-ca-certificates
  ```
- Use real PKI certificates in production — **never commit real ones**

---

## 🧭 Troubleshooting

| Problem | Solution |
|----------|-----------|
| `Permission denied` when updating certs | Rebuild container and verify mounts/permissions |
| `secret not found` | Check `SECRETS_CONFIG` and logs |
| Authentication failure | Verify `/run/secrets/server_creds` and Secret-Server/Platform URL |

---

## ⚠️ Security Notes

- The sidecar exposes **full secret fields** — secure access with HTTPS and network rules.
- Never store or commit actual credentials or production certs.

---

## 📄 License & Contributions

This is a **developer sample** — customize as needed.
Contributions are welcome, but please **exclude any sensitive data**.
