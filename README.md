**Project IronClad**

A self-healing IIoT edge gateway for remote industrial environments.

---

## The Problem

In Oil & Gas, a frozen gateway means a blind spot on a multimillion-dollar asset. Sending a technician to reboot a device on an offshore rig can cost thousands. IronClad eliminates that.

---

## Features

### Self-Healing Process Management

- Systemd `Type=notify` integration—service signals when ready
- Watchdog heartbeat every 60 seconds—freeze detected, service restarted in 4 seconds
- Circuit breaker after 5 failures triggers SMTP alert
- Hardware watchdog reboots device if OS hangs

### Data Persistence (Store & Forward)

- SQLite-backed buffering—writes to disk immediately
- Separate `/data` partition—database fills up, OS survives
- Zero data loss on crash or power failure

### Log Management

- Systemd Journal with priority levels—debug filtered, critical alerts
- 300MB cap with automatic rotation
- Prevents "Disk Full" bricking

### Encrypted Credentials

- `LoadCredentialEncrypted`—secrets injected at runtime
- Encrypted at rest, never in plain text
- Aligns with ISA/IEC 62443

### Resource Optimization

- `Nice=-10` CPU priority for telemetry
- Runs on low-cost edge hardware

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   HARDWARE LAYER                     │
│              Kernel Watchdog (softdog)               │
│         Physical reboot if OS hangs >20s             │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                   PROCESS LAYER                      │
│                     Systemd                          │
│  • WatchdogSec=60    • Restart=on-failure           │
│  • StartLimitBurst=5 • OnFailure=recovery.service   │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                 APPLICATION LAYER                    │
│                 Python Telemetry                     │
│  • sd_notify(READY/WATCHDOG)  • SQLite persistence  │
│  • journal.send() logging     • Encrypted creds     │
└─────────────────────────────────────────────────────┘
```

---

## File Structure

```
/etc/systemd/system/
├── ironclad.service          # Main telemetry service
├── ironclad-recovery.service # SMTP alert on failure

/opt/iiot_edge/
├── telemetry.py              # Main application
├── sos_alert.py              # Email alert script
├── data.db                   # SQLite telemetry store

/etc/credstore.encrypted/
└── EMAIL_PASSWORD.cred       # Encrypted credentials
```

---

## Quick Start

```bash
# Clone repo
git clone https://github.com/yourusername/ironclad.git

# Copy service files
sudo cp systemd/*.service /etc/systemd/system/

# Create encrypted credential
sudo systemd-creds encrypt --name=EMAIL_PASSWORD /dev/stdin /etc/credstore.encrypted/EMAIL_PASSWORD.cred

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable --now ironclad.service
```

---

## Usage

```bash
# Check status
systemctl status ironclad.service

# View logs
journalctl -u ironclad.service -f

# Query telemetry data
sqlite3 /opt/iiot_edge/data.db "SELECT * FROM readings ORDER BY ts DESC LIMIT 10;"

# Simulate crash (for testing)
touch /opt/iiot_edge/trigger_crash

# Simulate freeze (for testing)
touch /opt/iiot_edge/trigger_freeze
```

---

## Tech Stack

- Python 3
- Systemd (notify, watchdog, journal, credentials)
- SQLite
- LVM
- SMTP

---

## What I Learned

I'm in the Linux fundamentals phase of my journey toward Oil & Gas digital infrastructure. This project taught me that reliability isn't about code that doesn't crash—it's about systems that survive when it does.

---
