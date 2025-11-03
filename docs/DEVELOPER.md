# 💻 Developer Guide — Sidecar + nginx-proxy

This guide helps developers **run, modify, and understand** the Sidecar service and the `nginx-proxy` used for HTTPS in development.

---

## 🚀 What It Does

- The **Sidecar** connects to **Delinea Secret-Server/Platform**, fetches secrets, and serves them via a small HTTP API.
- The **nginx-proxy** adds HTTPS support during development.

---

## 🗂 Key Files

| File | Purpose |
|------|----------|
| `Dockerfile` | Builds the Python sidecar image |
| `docker-compose.yml` | Runs sidecar + nginx-proxy together |
| `nginx/nginx.conf` | Proxy routing and TLS configuration |
| `nginx/ssl/` | Dev certificates (`server.crt`, `server.key`) |
| `src/main.py` | Entry point for the sidecar |
| `src/delinea_secrets/secret_manager.py` | Handles credentials and polling secrets |
| `src/api/http_server.py` | Provides `/health`, `/secrets`, `/secrets/<name>` endpoints |

---

## ⚙️ How It Works

### Data Flow
```
[Delinea Secret-Server/Platform]
        ↑
     (polls)
        ↓
     [Sidecar] -- HTTP --> [nginx-proxy] -- HTTPS --> [Client]
```

- **Sidecar** polls secrets using credentials from `/run/secrets/server_creds`.
- Secrets are stored in memory.
- **nginx-proxy** listens on **port 8443**, handles HTTPS, and forwards traffic to the Sidecar on **port 8080**.

---

## 🧱 Run Instructions

### Run Both (Sidecar + Proxy)
```bash
docker-compose up --build sidecar nginx-proxy
```

### Run Only the Sidecar (Local)
```bash
python -m src.main
```

### Run Clients That Trust the Proxy Cert
The compose setup mounts the `nginx/ssl/server.crt` file into containers and runs:
```bash
update-ca-certificates
```

---

## 🌐 API Examples

From your **host**:
```bash
curl --cacert ./nginx/ssl/server.crt https://localhost:8443/health
```

From **another container**:
```bash
curl -k https://nginx-proxy:8443/health
```

---

## 🔐 Credentials and Config

| Location | Description |
|-----------|--------------|
| `/run/secrets/server_creds` | Contains credentials (key=value): <br>`SERVER_URL`, `SERVER_USERNAME`, `SERVER_PASSWORD` |
| `SECRETS_CONFIG` | Env var defining secrets to fetch <br>(JSON array or comma-separated IDs) |

Example:
```bash
$env:SECRETS_CONFIG = '[{"id":11126,"name":"mongo-secret","fields":"username,password"}]'
```

---

## 🧭 Common Tasks

| Task | How to Do It |
|------|---------------|
| Check logs | `docker-compose logs -f sidecar` |
| Verify sidecar health | `http://localhost:8080/health` |
| Debug HTTPS issues | Use `--cacert ./nginx/ssl/server.crt` or `-k` |
| Change returned fields | Update `SECRETS_CONFIG` fields |
| Adjust polling interval | Change `POLL_INTERVAL` env var |
| Add debug logs | Use `logger.info(...)` in code |

---

## 🧰 Troubleshooting

| Issue | Fix |
|--------|-----|
| `Permission denied` running `update-ca-certificates` | Run it as root before privilege drop |
| `curl` fails inside container | Ensure dev cert is installed or use `-k` |
| `secret not found` | Check `SECRETS_CONFIG` and sidecar logs |

---

## 🧪 Testing

- **Unit tests:** Use `pytest` to mock SDK calls and test secret fetching logic.
- **Integration tests:** Run `docker-compose up --build sidecar nginx-proxy` and test with `curl`.

---

## ⚠️ Best Practices

- Never commit real secrets or production certs.
- Use HTTPS and restrict network access in production.
- Store credentials only in Docker secrets or environment variables.

---

## ✅ Quick Reference Commands

```bash
# Start sidecar and proxy
docker-compose up --build sidecar nginx-proxy

# Check health
curl --cacert ./nginx/ssl/server.crt https://localhost:8443/health

# View logs
docker-compose logs -f sidecar
```

---

_This developer setup is for local use only. Secure configurations and real certificates are required for production._
