#!/bin/bash

# SSL Certificate Setup Script for DelineaPlatformSecretServer Sidecar (Linux)
# This creates self-signed certificates for HTTPS support

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 Setting up SSL certificates for Delinea Sidecar...${NC}"

# Create ssl directory
SSL_DIR="nginx/ssl"
mkdir -p "$SSL_DIR"

# Certificate configuration
CERT_SUBJECT="/C=US/ST=Virginia/L=Reston/O=DelineaSidecar/CN=sidecar-nginx"
DAYS=365
KEY_FILE="$SSL_DIR/server.key"
CERT_FILE="$SSL_DIR/server.crt"
CONF_FILE="$SSL_DIR/cert.conf"

echo -e "${BLUE}🔑 Generating SSL private key...${NC}"
openssl genrsa -out "$KEY_FILE" 2048

echo -e "${BLUE}📝 Creating certificate configuration...${NC}"
cat > "$CONF_FILE" << 'EOF'
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = Virginia
L = Reston
O = DelineaSidecar
CN = sidecar-nginx

[v3_req]
keyUsage = critical, digitalSignature, keyEncipherment, keyAgreement
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
basicConstraints = CA:FALSE

[alt_names]
DNS.1 = localhost
DNS.2 = sidecar-nginx
DNS.3 = nginx-proxy
IP.1 = 127.0.0.1
IP.2 = 0.0.0.0
EOF

echo -e "${BLUE}🔒 Generating SSL certificate...${NC}"
openssl req -new -x509 \
    -key "$KEY_FILE" \
    -out "$CERT_FILE" \
    -days "$DAYS" \
    -config "$CONF_FILE" \
    -extensions v3_req \
    -sha256

# Set proper permissions
echo -e "${BLUE}🔐 Setting secure file permissions...${NC}"
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

# Clean up config file
rm "$CONF_FILE"

echo -e "${GREEN}✅ SSL certificates generated successfully!${NC}"
echo ""
echo -e "${BLUE}📄 Certificate details:${NC}"
echo "----------------------------------------"
openssl x509 -in "$CERT_FILE" -noout -subject -issuer -dates
echo ""
echo "Subject Alternative Names:"
openssl x509 -in "$CERT_FILE" -noout -text | grep -A5 "Subject Alternative Name" || echo "  (Not displayed, but configured)"
echo ""
echo -e "${BLUE}📁 Files created:${NC}"
echo "   $KEY_FILE (private key - 600 permissions)"
echo "   $CERT_FILE (certificate - 644 permissions)"
echo ""
echo -e "${YELLOW}⚠️  Note: These are self-signed certificates for development.${NC}"
echo -e "${YELLOW}   For production, use certificates from a trusted CA.${NC}"
echo ""
echo -e "${GREEN}🎉 Setup complete! You can now use HTTPS with your Delinea Sidecar.${NC}"