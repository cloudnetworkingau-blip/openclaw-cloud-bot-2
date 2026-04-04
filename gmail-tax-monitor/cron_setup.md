# Cron Job Setup

## Automatic Daily Monitoring

To run the Gmail Tax Monitor daily at 9 AM, set up a cron job:

### Option 1: Using crontab
```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/gmail-tax-monitor && ./run_daily.sh >> /path/to/gmail-tax-monitor/logs/cron.log 2>&1
```

### Option 2: Using OpenClaw cron
```bash
# Create a cron job via OpenClaw
openclaw cron add --name "gmail-tax-monitor" --schedule "0 9 * * *" --command "cd /path/to/gmail-tax-monitor && ./run_daily.sh"
```

### Option 3: Systemd Service (Linux)
Create `/etc/systemd/system/gmail-tax-monitor.service`:
```ini
[Unit]
Description=Gmail Tax Monitor
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/path/to/gmail-tax-monitor
ExecStart=/path/to/gmail-tax-monitor/run_daily.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Then create a timer:
```ini
# /etc/systemd/system/gmail-tax-monitor.timer
[Unit]
Description=Run Gmail Tax Monitor daily at 9 AM

[Timer]
OnCalendar=daily 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable with:
```bash
sudo systemctl enable gmail-tax-monitor.timer
sudo systemctl start gmail-tax-monitor.timer
```

## Manual Testing
Test the monitor manually:
```bash
cd /path/to/gmail-tax-monitor
./run_daily.sh
```

## Log Rotation
To prevent log files from growing too large, add log rotation:

Create `/etc/logrotate.d/gmail-tax-monitor`:
```
/path/to/gmail-tax-monitor/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 your-username your-username
}
```

## Monitoring
Check if the cron job is running:
```bash
# Check crontab logs
grep CRON /var/log/syslog

# Check script logs
tail -f /path/to/gmail-tax-monitor/logs/cron.log

# Check last run
ls -la /path/to/gmail-tax-monitor/data/
```

## Troubleshooting
If the cron job doesn't run:
1. Check permissions: `chmod +x run_daily.sh`
2. Check paths in the script
3. Test manually first
4. Check cron service: `sudo service cron status`
5. Check logs: `grep CRON /var/log/syslog`