---

# 🛡️ Project IronClad: Self-Healing IIoT Edge Gateway

> **A Linux-native, fault-tolerant telemetry architecture designed for "Zero-Touch" remote environments (Oil & Gas / SCADA).**

## 📖 Executive Summary

In remote industrial environments (offshore rigs, pipelines), sending a technician to reboot a frozen gateway costs thousands of dollars ("truck rolls").

**Project IronClad** is a proof-of-concept **Resiliency Architecture** that leverages the Linux Kernel and Systemd to guarantee uptime without human intervention. Unlike standard Python scripts, IronClad integrates directly with the OS Init System (PID 1) to survive application crashes, process freezes, and storage exhaustion.

## 🏗️ Architecture

The system is built on a **3-Tier Defense Strategy**:

1. **Application Layer:** A Python Telemetry Agent using **SQLite** for atomic buffering and **Systemd Notification Sockets** (`sd_notify`) for heartbeat reporting.
2. **Process Layer:** A **Systemd Service Supervisor** configured with strict **Watchdogs** (`WatchdogSec`) and **Circuit Breakers** (`StartLimitBurst`) to detect freezes and restart the service automatically.
3. **Hardware Layer:** Kernel-level integration (`softdog`) to trigger a physical device reboot if the OS itself hangs.

## ✨ Key Features (The "God Tier" Tech)

### 1. 🔄 Unkillable Service Lifecycle (`Type=notify`)

* Uses **Inter-Process Communication (IPC)** to handshake with Systemd.
* The service is only marked "Active" after the database connection is verified (`READY=1`).
* Dynamic status updates (`STATUS=Processing...`) visible in `systemctl status` without reading logs.

### 2. ⏱️ Watchdog & Freeze Detection

* **Software Watchdog:** If the main loop freezes (e.g., stuck network call) for >10 seconds, Systemd sends `SIGABRT` and restarts the service.
* **Hardware Watchdog:** If Systemd fails, the Linux Kernel triggers a hardware reset.

### 3. 💾 Storage Forensics & Isolation (LVM)

* **Data Silo:** Telemetry data is isolated on a dedicated **Logical Volume (LVM)** (`/opt/iiot_edge`). If the database fills up, it cannot crash the Root OS.
* **Structured Logging:** Replaces `print()` with **Systemd Journal Binary Logging**. Supports metadata filtering (`DEVICE_ID=pump01`) and Priority Levels (Alert vs Info).
* **Forensic Persistence:** Logs are configured to survive reboots (`Storage=persistent`) with strict quotas (`SystemMaxUse=50M`) to prevent disk exhaustion.

### 4. 🔐 Military-Grade Security

* **No Hardcoded Secrets:** Credentials are managed via **Systemd LoadCredentialEncrypted**.
* **Hardware Binding:** Secrets are encrypted on-disk and only decrypted into a secure RAM filesystem (`tmpfs`) by Systemd at runtime.
* **Resource Prioritization:** Service runs with `Nice=-10` to guarantee CPU cycles during high-load system updates.

---

## 🚀 Installation & Deployment

### Prerequisites

- Linux VM (Ubuntu/Debian/RHEL) or Raspberry Pi.
- Python 3 + `systemd-python` library.

### 1. Setup the Environment

```bash
# Install dependencies
sudo apt update && sudo apt install python3-systemd lvm2

# Clone the repo (Simulated)
git clone https://github.com/YOUR_USERNAME/ironclad-iiot.git
cd ironclad-iiot

```

### 2. Deploy to Linux Paths

We separate code (`/opt`) from config (`/etc`).

```bash
# 1. Install the Agent
sudo mkdir -p /opt/iiot_edge
sudo cp src/*.py /opt/iiot_edge/

# 2. Install the Service Units
sudo cp config/*.service /etc/systemd/system/

# 3. Reload Systemd
sudo systemctl daemon-reload

```

### 3. Configure Security (Optional)

If using `systemd-creds` (Systemd v250+):

```bash
# Encrypt your password
sudo systemd-creds encrypt --name=gmail_pass - /etc/credstore.encrypted/gmail_pass.cred

```

### 4. Ignite

```bash
sudo systemctl enable --now ironclad.service

```

---

## 🧪 Testing & Chaos Engineering

This project includes "Self-Destruct" triggers to verify the recovery architecture.

### Test 1: The Crash (Process Failure)

Simulate a fatal code error.

```bash
# Create the trigger file
sudo touch /opt/iiot_edge/trigger_crash

# Watch it die and resurrect
watch systemctl status ironclad

```

- **Expected Result:** Service fails, waits 2s (`RestartSec`), and restarts automatically.

### Test 2: The Freeze (Watchdog Timeout)

Simulate a hung process (infinite loop).

```bash
sudo touch /opt/iiot_edge/trigger_freeze

```

- **Expected Result:** Service stays "Active" for 10s, then Systemd kills it (Watchdog Timeout) and restarts it.

---

## 🛠️ Project Structure

```text
ironclad-iiot/
├── config/
│   ├── ironclad.service          # The Main Brain (Watchdogs, Nice Level)
│   ├── ironclad-recovery.service # The Paramedic (Email Alerts)
│   └── journald.conf             # Log Retention Policies
├── src/
│   ├── telemetry.py              # The Agent (SQLite + Notification Socket)
│   └── sos_alert.py              # The Recovery Script
├── RUNBOOK.md                    # Operational SOPs for Support Teams
└── README.md                     # This file

```

## 🔮 Future Roadmap

- [ ] **Azure IoT Hub:** Forwarding SQLite buffer to the Cloud.
- [ ] **Terraform:** Automating the VM provisioning.
- [ ] **Docker:** Containerizing the agent (Hybrid Architecture).

---

_Built by [Your Name] as part of the "Top 1%" DevOps Architecture Portfolio._
