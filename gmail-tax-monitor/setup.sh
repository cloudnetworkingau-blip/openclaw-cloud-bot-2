#!/bin/bash

# Gmail Tax Monitor Setup Script

echo "🚀 Setting up Gmail Tax Monitor..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Make scripts executable
chmod +x setup_auth.py tax_monitor.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to Google Cloud Console: https://console.cloud.google.com/"
echo "2. Create a new project"
echo "3. Enable Gmail API"
echo "4. Create OAuth 2.0 Desktop app credentials"
echo "5. Download credentials.json and place it in this directory"
echo ""
echo "🔐 Then run: ./setup_auth.py"
echo ""
echo "📅 To run daily monitoring, add to crontab:"
echo "0 9 * * * cd $(pwd) && ./venv/bin/python3 tax_monitor.py"