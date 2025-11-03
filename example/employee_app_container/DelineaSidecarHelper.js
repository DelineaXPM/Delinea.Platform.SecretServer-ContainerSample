const axios = require('axios');
const https = require('https');
const fs = require('fs');

// Create HTTPS agent with the CA certificate
const httpsAgent = new https.Agent({
  ca: fs.readFileSync('/usr/local/share/ca-certificates/nginx-proxy.crt'),
  rejectUnauthorized: true
});

let cachedSecret = null;
let cacheTime = 0;
const CACHE_DURATION_MS = 60 * 1000; // 1 minute cache

async function getSecretFromDelineaSidecar(secretNameOrID) {
  const now = Date.now();
  if (!cachedSecret || (now - cacheTime) > CACHE_DURATION_MS) {
    const url = `https://nginx-proxy:8443/secrets/${encodeURIComponent(secretNameOrID)}`;
    const resp = await axios.get(url, { httpsAgent });
    cachedSecret = resp.data;
    cacheTime = now;
  }
  return cachedSecret;
}

// Export the function so callers can import and use it directly
module.exports = { getSecretFromDelineaSidecar };