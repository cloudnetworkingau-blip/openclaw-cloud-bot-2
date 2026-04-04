# 🚀 Gmail Tax Monitor - Complete Setup Guide

## 📋 **What This System Does**
- Monitors your Gmail daily for tax-related emails
- Automatically saves invoices and attachments
- Organizes files by category (ATO, ASIC, SMSF, Bills, etc.)
- Marks processed emails and adds labels
- Runs securely using OAuth 2.0 (no password storage)

## 🔐 **Step-by-Step Setup**

### **Step 1: Google Cloud Console Setup**
1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
2. **Create a new project**: Click "Select a project" → "New Project"
   - Name: `Gmail-Tax-Monitor-2026`
   - Location: Your organization (or no organization)
3. **Enable Gmail API**:
   - Navigation menu → "APIs & Services" → "Library"
   - Search for "Gmail API" → Click "Enable"
4. **Configure OAuth Consent Screen**:
   - "APIs & Services" → "OAuth consent screen"
   - User Type: "External" (for personal use)
   - App name: `Gmail Tax Monitor`
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `.../auth/gmail.readonly` and `.../auth/gmail.modify`
   - Test users: Add your email
   - Save and continue through all steps

### **Step 2: Create OAuth Credentials**
1. **Create credentials**:
   - "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Desktop app"
   - Name: `Gmail Tax Monitor Desktop`
2. **Download credentials**:
   - Click the download icon next to your new client ID
   - Save as `credentials.json`
   - Place in the `gmail-tax-monitor` folder

### **Step 3: Local Setup**
```bash
# Navigate to the folder
cd /path/to/gmail-tax-monitor

# Run setup script
./setup.sh

# Authenticate (this will open a browser)
./setup_auth.py
```
- When `setup_auth.py` runs, it will open a browser window
- Log in with your Google account
- Grant the requested permissions
- The script will save authentication tokens locally

### **Step 4: Test the System**
```bash
# Run a test scan
./run_daily.sh

# Check the results
ls -la data/
cat logs/monitor_*.log
```

### **Step 5: Set Up Daily Automation**
Choose one method:

**Option A: Cron Job (Recommended)**
```bash
# Edit crontab
crontab -e

# Add this line (adjust the path)
0 9 * * * cd /home/ubuntu/.openclaw/workspace/gmail-tax-monitor && ./run_daily.sh >> logs/cron.log 2>&1
```

**Option B: OpenClaw Cron**
```bash
# If using OpenClaw's cron system
openclaw cron add --name "tax-monitor" --schedule "0 9 * * *" --command "cd /path/to/gmail-tax-monitor && ./run_daily.sh"
```

## 📁 **Folder Structure**
```
gmail-tax-monitor/
├── credentials.json          # Google OAuth credentials (you add this)
├── token.pickle             # Authentication tokens (auto-generated)
├── setup_auth.py           # Initial authentication
├── tax_monitor.py          # Main monitoring script
├── config.py              # Configuration settings
├── setup.sh              # Setup script
├── run_daily.sh          # Daily runner
├── README.md            # Overview
├── SETUP_GUIDE.md       # This guide
├── cron_setup.md        # Cron job instructions
├── data/               # Saved invoices organized by category/date
│   ├── ATO/
│   ├── ASIC/
│   ├── SMSF/
│   ├── Bills/
│   └── ...
└── logs/               # Log files
```

## ⚙️ **Customization**

### **Edit config.py to:**
1. **Add more keywords**: Modify `TAX_KEYWORDS` list
2. **Change file types**: Update `INVOICE_FILE_TYPES`
3. **Adjust search period**: Change `DAYS_TO_CHECK`
4. **Modify organization**: Update `get_storage_path()` function

### **Add specific senders:**
```python
PRIORITY_SENDERS = [
    'ato.gov.au',
    'your-accountant.com',
    'your-bank.com.au',
    # Add more...
]
```

## 🔒 **Security Features**
- **OAuth 2.0**: No password storage
- **Read-only access**: Can't send emails or modify content beyond labeling
- **Local storage**: All data stays on your machine
- **Encryption option**: Can add GPG encryption for sensitive files
- **Token refresh**: Automatic token renewal

## 🐛 **Troubleshooting**

### **Authentication Issues**
```bash
# Delete tokens and re-authenticate
rm -f token.pickle
./setup_auth.py
```

### **Permission Errors**
- Ensure `credentials.json` is in the correct folder
- Check Google Cloud Console for enabled APIs
- Verify test user email is added in OAuth consent screen

### **Script Not Running**
```bash
# Check permissions
chmod +x *.py *.sh

# Test manually
./run_daily.sh

# Check logs
tail -f logs/monitor_*.log
```

### **Missing Dependencies**
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 **Monitoring & Maintenance**

### **Check Daily Runs**
```bash
# View recent logs
tail -n 50 logs/monitor_*.log

# Check saved files
find data/ -type f -name "*.pdf" | wc -l

# Check disk usage
du -sh data/
```

### **Monthly Cleanup**
```bash
# Archive old files (optional)
tar -czf data_archive_$(date +%Y%m).tar.gz data/* --exclude="data/current_month"
```

### **Update Configuration**
Review `config.py` quarterly to:
1. Update tax keywords
2. Add new sender domains
3. Adjust file retention policies

## 🆘 **Support**
If you encounter issues:
1. Check the logs in `logs/` directory
2. Verify Google Cloud Console settings
3. Ensure Python dependencies are installed
4. Check cron job syntax and permissions

## ✅ **Success Checklist**
- [ ] Google Cloud project created
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured
- [ ] `credentials.json` downloaded and placed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Authentication successful (`token.pickle` created)
- [ ] Test run completed
- [ ] Cron job scheduled
- [ ] First daily run verified

---

**Next**: After setup, the system will run daily at 9 AM, monitoring for tax emails and saving attachments automatically. Check the `data/` folder periodically for organized invoices and documents.