Quick examples — curl
--------------------
Below are small examples using `curl` (bash) and `curl.exe` (PowerShell/Git for Windows). They cover local (HTTP) access to the sidecar and HTTPS access via the `nginx-proxy` (development cert).
From the host — local HTTP (sidecar binds to 127.0.0.1:8080 by default):

```bash
```
# health
curl -sS http://127.0.0.1:8080/health

# list secrets
curl -sS http://127.0.0.1:8080/secrets
# fetch a secret (example name)
curl -sS http://127.0.0.1:8080/secrets/secret-name
# fetch a secret (example ID)
curl -sS http://127.0.0.1:8080/secrets/12345

```
Via the nginx-proxy — HTTPS (development certificate)

If you want to validate the proxy cert rather than skipping verification, pass the development cert to curl. From the repository root:

```bash
```
# health (validate with dev cert)
curl -sS --cacert ./nginx/ssl/server.crt https://localhost:8443/health

# or skip verification (not recommended except for quick tests)
curl -sSk https://localhost:8443/health
PowerShell (Windows) — using bundled curl.exe (or Git Bash) to call the proxy:

```powershell
```
# use curl.exe so PowerShell doesn't invoke Invoke-WebRequest
curl.exe --cacert .\nginx\ssl\server.crt https://localhost:8443/health
# or (skip cert verification)
curl.exe -k https://localhost:8443/health
Inside containers (quick):

```powershell
```
# run a curl command inside the sidecar container (HTTP)
docker-compose exec sidecar curl -sS http://localhost:8080/health

# run a curl command inside the nginx-proxy container (HTTPS)
docker-compose exec nginx-proxy curl -sSk https://localhost:8443/health
These examples are meant for development and troubleshooting. In production, use proper PKI-signed certificates and do not skip certificate verification.

Notes on URLs when using `nginx-proxy`:
- From your host/machine use https://localhost:8443 to reach the proxy.
- From another container on the same Docker network use https://nginx-proxy:8443 to reach the proxy by service name.

Examples above use those conventions: host examples target `https://localhost:8443`, in-container proxy checks target `https://nginx-proxy:8443`.