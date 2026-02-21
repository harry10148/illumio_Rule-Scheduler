# Illumio Rule Scheduler User Manual

Welcome to the User Manual for the Illumio Rule Scheduler. This document provides a complete guide on how to configure, operate, and deploy the application, along with examples and operational principles.

## Table of Contents
1. [Overview & Operating Principles](#overview--operating-principles)
2. [Operating Modes](#operating-modes)
    - [Web GUI Mode](#web-gui-mode)
    - [CLI Mode](#cli-mode)
    - [Daemon Mode](#daemon-mode)
3. [Features & Capabilities](#features--capabilities)
4. [Configuration](#configuration)
5. [Schedule Examples](#schedule-examples)
6. [Deployment Guide](#deployment-guide)

---

## Overview & Operating Principles
The **Illumio Rule Scheduler** automates the enabling and disabling of Illumio policy rules and RuleSets on a predefined schedule. 

### How it works
1. **Targeting**: You select Illumio RuleSets or child rules and define their active "windows" or an "expiration" time.
2. **Monitoring Engine**: A daemon runs in the background. By default, it wakes up every 300 seconds (5 minutes) to evaluate all schedules.
3. **Execution**: If the current time falls inside a configured schedule window, the engine ensures the object is set to `enabled=True` via the PCE REST API. If it is outside the window, it sets it to `enabled=False`.
4. **Provisioning**: The script utilizes Illumio API's dependency-aware endpoints. Before issuing a provision command, it securely discovers all object dependencies, mitigating "unprovisioned dependencies" errors.
5. **Transparency**: The scheduler will append a note with the text `[📅 Schedule: ...]` or `[⏳ Expiration: ...]` into the `description` field of the managed object on the PCE so administrators have visibility in the native console.

---

## Operating Modes

There are three main ways to interact with the application.

### Web GUI Mode
Launch the Flask-powered Web GUI for a complete visual experience:
```bash
python illumio_scheduler.py --gui --port 5000
```
- **Browse & Add**: Navigate through RuleSets and assign schedules visually. The left pane is fully resizable and the application naturally spans ultrawide monitors.
- **Schedules Tab**: Review your master list of scheduled policies. Select multiple items to bulk delete.
- **Logs**: A terminal view straight from your browser to manually execute a run and observe logs.
- **Settings**: Safely store PCE API tokens, select your UI language (English/Chinese), and toggle Light/Dark Mode.

### CLI Mode
For SSH/terminal environments without graphical support.
```bash
python illumio_scheduler.py
```
This drops you into an interactive menu:
```text
=== Illumio Scheduler ===
0. Settings
1. Schedule Management (Browse/List/Edit/Delete)
2. Run Check Now
3. Open Web GUI
q. Quit
```
You can type `a` in Schedule Management to add new schedules, or `e <ID>` to edit the time windows.

### Daemon Mode
For background execution, ensuring schedules are constantly monitored and applied.
```bash
python illumio_scheduler.py --monitor
```
*Note: Consult the [Deployment Guide](#deployment-guide) for running this permanently as a service.*

---

## Features & Capabilities

- **Recurring Schedules**: Set rules to be active only on certain days of the week between specific hours.
  - *Example*: Monday to Friday, 08:00 to 18:00.
  - Supports cross-midnight shifts (e.g., 22:00 to 06:00).
- **One-Time Expirations**: Set a specific date and time for a rule to expire. After that time passes, the rule is disabled and the schedule is automatically purged from the local database.
- **Draft Safety**: The scheduler will not try to schedule a rule that hasn't been provisioned yet.
- **i18n Translation & Theming**: Completely bilingual support (English & Traditional Chinese) and both visually stunning Light/Dark themes derived from Illumio Brand Guidelines natively into the Web GUI.

---

## Configuration

To communicate with the Illumio PCE, open the Settings menu (via the Web GUI or CLI Menu #0) and enter the following keys. These are securely saved in `config.json`.

| Field | Description |
|---|---|
| **PCE URL** | Full FQDN of your PCE (e.g. `https://pce.local:8443`) |
| **Org ID** | Your Organization ID (usually `1`) |
| **API Key** | Generated from your user profile on the PCE (`api_xxx`) |
| **API Secret** | Generated alongside the API Key |

*Requirement*: Your API Key must have at least **Ruleset Provisioner** or **Global Organization Owner** privileges.

---

## Schedule Examples

### Example 1: Standard Office Hours Access
You want a RuleSet to only be active while developers are in the office.
- **Target**: RuleSet `Dev Access`
- **Type**: Recurring
- **Action**: Allow (Enable in window)
- **Days**: Monday, Tuesday, Wednesday, Thursday, Friday
- **Start**: `08:00` | **End**: `18:00`
- **Result**: RuleSet is ON from 8 AM to 6 PM on weekdays. OFF at all other times.

### Example 2: Temporary Vendor Access
A vendor needs access until the end of the month.
- **Target**: RuleSet `Vendor RDP`
- **Type**: One-Time Expiration
- **Expire At**: `2025-12-31 23:59`
- **Result**: RuleSet is left ON until midnight on Dec 31st, 2025. After that, the rule is disabled and removed from the watch list.

---

## Deployment Guide

To ensure high availability, use the supplied deployment scripts located in the `deploy/` directory.

### Windows
We utilize NSSM to run the python script as a native Windows service.
1. Download `nssm.exe`.
2. Open PowerShell as Administrator.
3. Run:
   ```powershell
   .\deploy\deploy_windows.ps1 -NssmPath "C:\path\to\nssm.exe"
   ```
4. A Windows Service named `IllumioScheduler` will be created and started. It automatically handles error logging and restarts.

### Linux
We provide a standard Systemd unit file.
1. Copy the unit file:
   ```bash
   sudo cp deploy/illumio-scheduler.service /etc/systemd/system/
   ```
2. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now illumio-scheduler
   ```
3. Watch the logs:
   ```bash
   sudo journalctl -u illumio-scheduler -f
   ```

*End of Document*
