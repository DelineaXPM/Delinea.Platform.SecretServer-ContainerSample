#!/bin/bash

# SSL Certificate Setup Script for DelineaPlatformSecretServer Sidecar (Windows Compatible)
# This creates self-signed certificates for HTTPS support

set -e

echo "🔐 Setting up SSL certificates for Delinea Sidecar..."

# Create ssl directory
mkdir -p nginx/ssl
cd nginx/ssl

# Certificate configuration
CERT_SUBJECT="//C=US\ST=Virginia\L=Reston\O=DelineaSidecar\CN=sidecar-nginx"
DAYS=365

echo "📝 Generating SSL private key..."
openssl genrsa -out server.key 2048

echo "📝 Creating certificate configuration..."
cat > cert.conf << EOF
[req]
distinguished_name = req
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = localhost
DNS.2 = sidecar-nginx
DNS.3 = nginx-proxy
IP.1 = 127.0.0.1
IP.2 = 0.0.0.0
EOF

echo "📝 Generating SSL certificate..."
openssl req -new -x509 -key server.key -out server.crt -days $DAYS -subj "$CERT_SUBJECT" -extensions v3_req -config cert.conf

# Clean up config file
rm cert.conf

# Set proper permissions (if chmod works)
chmod 600 server.key 2>/dev/null || echo "Note: Could not set key permissions (Windows)"
chmod 644 server.crt 2>/dev/null || echo "Note: Could not set cert permissions (Windows)"

echo "✅ SSL certificates generated successfully!"
echo ""
echo "📄 Certificate details:"
openssl x509 -in server.crt -text -noout | grep -A2 "Subject:" || echo "Certificate created successfully"
openssl x509 -in server.crt -text -noout | grep -A5 "DNS:" || echo "With proper DNS names"

echo ""
echo "📁 Files created:"
echo "   nginx/ssl/server.key (private key)"
echo "   nginx/ssl/server.crt (certificate)"

echo ""
echo "⚠️  Note: These are self-signed certificates for development."
echo "   For production, use certificates from a trusted CA."

cd ../../