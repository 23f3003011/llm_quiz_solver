#!/bin/bash
set -e

echo "=== Starting Build Process ==="

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🎮 Installing Playwright browsers..."
python -m playwright install chromium
python -m playwright install-deps chromium

echo "✅ Build completed successfully!"
