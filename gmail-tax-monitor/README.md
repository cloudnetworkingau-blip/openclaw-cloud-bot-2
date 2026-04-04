# Gmail Tax Monitor

## Overview
Secure system to monitor tax-related emails and save invoices using Gmail API.

## Setup Instructions

### 1. Google Cloud Console Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "Gmail-Tax-Monitor-2026")
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it

### 2. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Configure consent screen:
   - Application type: "Desktop app"
   - Name: "Gmail Tax Monitor"
   - Add your email as a test user
4. Download credentials as `credentials.json`

### 3. Install Required Packages
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 4. Configure the Application
1. Place `credentials.json` in the project root
2. Run the setup script to authenticate:
```bash
python3 setup_auth.py
```

## Features
- Monitors emails for tax-related keywords
- Downloads and organizes invoice attachments
- Categorizes by sender (ATO, ASIC, SMSF, etc.)
- Stores in organized folder structure
- Runs daily via cron job

## Security Notes
- OAuth tokens stored locally (not shared)
- Read-only access to Gmail
- No password storage
- Encrypted local storage option available