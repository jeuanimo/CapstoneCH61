#!/usr/bin/env bash
# Build script for Render.com deployment
# This script runs during the build phase

set -o errexit  # Exit on error

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --no-input

echo "=== Running database migrations ==="
python manage.py migrate --no-input

echo "=== Build complete ==="
