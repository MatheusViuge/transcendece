#!/bin/sh
set -eu

CERT_DIR=/etc/nginx/certs
KEY_FILE="$CERT_DIR/server.key"
CERT_FILE="$CERT_DIR/server.crt"

mkdir -p "$CERT_DIR"

if [ ! -s "$KEY_FILE" ] || [ ! -s "$CERT_FILE" ]; then
  echo "[proxy] generating local self-signed TLS certificate"
  openssl req \
    -x509 \
    -nodes \
    -days 365 \
    -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
  chmod 600 "$KEY_FILE"
fi
