# Illumio Rule Scheduler (v4.2.0)

![Version](https://img.shields.io/badge/Version-v4.2.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-gold?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen)


> [English](#english) | [繁體中文](#繁體中文)

---

## English

An automated rule scheduling tool for **Illumio Core (PCE)**. Supports **Web GUI**, **CLI**, and **Daemon** modes. Core engine uses only Python standard library — Flask is the only optional dependency (for Web GUI only).

---

## ✨ Features

| Feature | Description |
|---|---|
| 📅 **Recurring Schedule** | Enable/disable rules on a weekly schedule (supports cross-midnight, e.g. 22:00–06:00) |
| ⏳ **Auto-Expiration** | One-time rules that auto-disable and self-delete after a set time |
| 🖥️ **Web GUI + CLI** | Flask-powered Web GUI (auto-opens browser); ANSI CLI for SSH/terminal |
| 🌐 **i18n Support** | Language toggle between English (default) and Traditional Chinese |
| 👁️ **Visual Indicators** | `PROV` state (ACTIVE/DRAFT), symbols (★ = RS scheduled, ● = Child rule) |
| 🛡️ **Draft Safety** | Prevents scheduling of unprovisioned (draft-only) rules |
| 📝 **Note Integration** | Automatically writes schedule status to Illumio `description` field |
| 🔄 **Dependency-Aware Provisioning** | Discovers and includes all PCE dependencies before provisioning |
| 🛡️ **Zero Core Dependencies** | Core engine and CLI use only Python standard library |

---

## 📁 Project Structure

```
illumio_Rule-Scheduler/
├── illumio_scheduler.py          # Entry point (CLI / GUI / Daemon)
├── src/
│   ├── __init__.py
│   ├── core.py                   # Core engine (API, DB, scheduling logic)
│   ├── cli_ui.py                 # CLI interactive interface
│   ├── gui_ui.py                 # Flask Web GUI (dark theme SPA)
│   └── i18n.py                   # Internationalisation (EN/ZH string tables)
├── deploy/
│   ├── deploy_windows.ps1        # Windows NSSM service deployment
│   └── illumio-scheduler.service # Linux systemd unit file
├── config.json                   # API settings (generated at runtime, git-ignored)
├── rule_schedules.json           # Schedule database (generated at runtime, git-ignored)
└── README.md
```

---

## 🛠️ Installation

**Core requirement**: Python 3.8+

**Web GUI** (optional): `pip install flask`
> CLI mode works without Flask. If Flask is not installed, the `--gui` flag will display install instructions instead.

**Linux / macOS**:
```bash
sudo mkdir -p /opt/illumio_scheduler
cd /opt/illumio_scheduler
# Copy project files here
chmod +x illumio_scheduler.py
pip install flask    # optional, for Web GUI only
```

**Windows**:
1. Install [Python 3](https://www.python.org/downloads/) (check "Add to PATH")
2. Place the project directory anywhere (e.g. `C:\illumio_scheduler`)
3. Optionally: `pip install flask` for Web GUI

---

## 🚀 Usage

### Web GUI Mode (recommended for desktop)
```bash
python illumio_scheduler.py --gui
```
- Starts Flask server on `http://localhost:5000`
- Auto-opens browser
- Dark-themed single-page application

### CLI Mode (recommended for SSH / terminal)
```bash
python illumio_scheduler.py
```
**Main Menu:**
```
=== Illumio Scheduler v4.2 (Hybrid UI) ===
0. Configure API
1. Schedule Management (Browse/List/Edit/Delete)
2. Run Check Now
3. Open Web GUI
4. Language [EN]
q. Quit
```

### Daemon Mode (background monitoring)
```bash
python illumio_scheduler.py --monitor
```
> Runs the schedule engine in a loop (default: every 300 seconds)

---

## ⚙️ Background Service Deployment

### Windows (NSSM recommended)

1. Download [NSSM](http://nssm.cc/download)
2. Run as **Administrator**:
   ```powershell
   .\deploy\deploy_windows.ps1 -NssmPath "C:\path\to\nssm.exe"
   ```
3. The service installs and starts automatically (name: `IllumioScheduler`)

**Alternative: Task Scheduler**
- Create Task → Trigger: At system startup → Action: `python illumio_scheduler.py --monitor`

### Linux (Systemd)

```bash
sudo cp deploy/illumio-scheduler.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now illumio-scheduler
sudo journalctl -u illumio-scheduler -f
```

---

## 🏗️ Architecture (For Developers)

### Module Overview

| Module | Responsibility |
|---|---|
| `illumio_scheduler.py` | Entry point: routes to CLI (`default`), Web GUI (`--gui`), or Daemon (`--monitor`) |
| `src/core.py` | Core engine: `ConfigManager`, `ScheduleDB`, `PCEClient`, `ScheduleEngine` — zero external deps |
| `src/cli_ui.py` | CLI interactive menu: browse/add/edit/delete schedules, language selector |
| `src/gui_ui.py` | Flask Web GUI: REST API endpoints + embedded HTML/CSS/JS SPA |
| `src/i18n.py` | i18n string tables (EN, ZH). Call `t('key')` to translate |

### Core Classes (`src/core.py`)

| Class | Description |
|---|---|
| `ConfigManager` | Loads/saves `config.json` (PCE URL, org, API key/secret) |
| `ScheduleDB` | JSON-based schedule database (`rule_schedules.json`) |
| `PCEClient` | Illumio PCE REST API client using `urllib.request` (zero deps) |
| `ScheduleEngine` | The scheduling logic: compares current time against schedules, toggles rules |

### Web GUI API Endpoints (`src/gui_ui.py`)

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Serve the SPA HTML page |
| `/api/rulesets` | GET | List all rulesets (supports `?q=keyword` search) |
| `/api/rulesets/<id>` | GET | Get single ruleset with all rules |
| `/api/schedules` | GET | List all configured schedules |
| `/api/schedules` | POST | Create or overwrite a schedule |
| `/api/schedules/<href>` | DELETE | Delete a schedule and clean up notes |
| `/api/check` | POST | Run manual policy check |
| `/api/config` | GET/POST | Get or save API configuration |
| `/api/stop` | POST | Graceful server shutdown |

### PCE API Integration

- **API Version**: v2 (Illumio Core 25.2+)
- **Authentication**: HTTP Basic Auth via `Authorization` header
- **SSL**: Disabled verification (`ssl.CERT_NONE`) for self-signed PCE certificates
- **Provisioning**: Dependency-aware — calls `POST /sec_policy/draft/dependencies` before provisioning to include all required objects

### i18n System (`src/i18n.py`)

```python
from src.i18n import t, set_lang, get_lang

set_lang('zh')        # Switch to Traditional Chinese
set_lang('en')        # Switch to English (default)
print(t('app_title')) # Get translated string
```

To add a new language, add a new key in `_STRINGS` dict (e.g. `'ja'`) with all the same keys as `'en'`.

### Schedule Data Format (`rule_schedules.json`)

```json
{
  "/orgs/1/sec_policy/draft/rule_sets/206": {
    "type": "recurring",
    "name": "K8sNode | Kubernetes",
    "is_ruleset": true,
    "action": "allow",
    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "start": "08:00",
    "end": "18:00",
    "detail_rs": "K8sNode | Kubernetes",
    "detail_src": "All",
    "detail_dst": "All",
    "detail_svc": "All",
    "detail_name": "K8sNode | Kubernetes"
  }
}
```

| Field | Description |
|---|---|
| `type` | `recurring` or `one_time` |
| `is_ruleset` | `true` if scheduling the entire RuleSet, `false` for a single rule |
| `action` | `allow` (enable in window) or `block` (disable in window) |
| `days` | Array of day names (e.g. `["Monday", "Friday"]`) |
| `start` / `end` | Time window in `HH:MM` format (supports cross-midnight) |
| `expire_at` | ISO datetime for one-time expiration (e.g. `2025-12-31T23:59`) |

---

## ⚠️ Notes & Troubleshooting

1. **Clock accuracy** — Ensure the host timezone is correct (`timedatectl` / Windows time settings)
2. **API permissions** — The API Key must have **Global Admin** or **Ruleset Provisioner** privileges
3. **Provisioning scope** — Provisioning is per-RuleSet; the tool auto-discovers dependencies to avoid conflicts
4. **Check interval** — Default is 300 seconds; adjust with env var `ILLUMIO_CHECK_INTERVAL=<seconds>`
5. **Security** — API credentials are stored in plaintext in `config.json`; set appropriate directory permissions
6. **Flask not found** — If you see "Flask is required", install with `pip install flask`. CLI works without it.

---

## 📄 License

This project is provided as-is for internal use.

---

<br>

## 繁體中文

**Illumio Core (PCE)** 自動化規則排程工具。支援 **Web GUI**、**CLI** 及 **Daemon** 模式。核心引擎僅使用 Python 標準程式庫，Flask 為唯一的選用依賴（僅 Web GUI 需要）。

---

## ✨ 功能特性

| 功能 | 說明 |
|---|---|
| 📅 **週期排程** | 指定星期與時段自動啟停規則（支援跨午夜，如 22:00–06:00） |
| ⏳ **自動過期** | 設定失效時間，時間到後自動關閉並刪除排程 |
| 🖥️ **Web GUI + CLI** | Flask 驅動的 Web GUI（自動開啟瀏覽器）；SSH 環境使用 CLI 選單 |
| 🌐 **多語系** | 支援語系切換：英文（預設）與繁體中文 |
| 👁️ **視覺指標** | `PROV` 狀態（ACTIVE/DRAFT），符號（★ = 規則集排程，● = 子規則排程） |
| 🛡️ **草稿保護** | 阻擋對未發布（僅存於草稿）的規則進行排程，減少錯誤 |
| 📝 **Note 整合** | 自動將排程狀態寫入 Illumio Description 欄位 |
| 🔄 **依賴感知發布** | 發布前自動探索 PCE 依賴項，避免因缺少依賴而失敗 |
| 🛡️ **零核心依賴** | 核心引擎與 CLI 僅使用 Python 標準程式庫 |

---

## 📁 專案結構

```
illumio_Rule-Scheduler/
├── illumio_scheduler.py          # 程式進入點 (CLI / GUI / Daemon)
├── src/
│   ├── __init__.py
│   ├── core.py                   # 核心引擎（API, DB, 排程邏輯）
│   ├── cli_ui.py                 # CLI 互動介面
│   ├── gui_ui.py                 # Flask Web GUI（深色主題 SPA）
│   └── i18n.py                   # 國際化（EN/ZH 字串表）
├── deploy/
│   ├── deploy_windows.ps1        # Windows NSSM 服務部署腳本
│   └── illumio-scheduler.service # Linux systemd unit 檔案
├── config.json                   # API 設定（執行時產生，已加入 .gitignore）
├── rule_schedules.json           # 排程資料庫（執行時產生，已加入 .gitignore）
└── README.md
```

---

## 🛠️ 安裝

**基本需求**：Python 3.8+

**Web GUI**（選用）：`pip install flask`
> CLI 模式不需要 Flask。若未安裝 Flask，使用 `--gui` 時會顯示安裝指令。

**Linux / macOS**：
```bash
sudo mkdir -p /opt/illumio_scheduler
cd /opt/illumio_scheduler
# 將專案檔案複製至此目錄
chmod +x illumio_scheduler.py
pip install flask    # 選用，僅 Web GUI 需要
```

**Windows**：
1. 安裝 [Python 3](https://www.python.org/downloads/)（勾選「Add to PATH」）
2. 將專案目錄放至任意位置（如 `C:\illumio_scheduler`）
3. 選用：`pip install flask` 安裝 Web GUI

---

## 🚀 使用方式

### Web GUI 模式（推薦桌面環境）
```bash
python illumio_scheduler.py --gui
```
- 啟動 Flask 服務於 `http://localhost:5000`
- 自動開啟瀏覽器
- 深色主題單頁應用程式

### CLI 模式（推薦 SSH / 終端機）
```bash
python illumio_scheduler.py
```
**主選單：**
```
=== Illumio Scheduler v4.2 (Hybrid UI) ===
0. Configure API（設定 API）
1. Schedule Management（排程管理）
2. Run Check Now（立即檢查）
3. Open Web GUI（開啟 Web GUI）
4. Language [EN]（語系切換）
q. Quit（離開）
```

### Daemon 模式（背景監控）
```bash
python illumio_scheduler.py --monitor
```
> 以迴圈方式執行排程引擎（預設每 300 秒）

---

## ⚙️ 背景服務部署

### Windows（建議使用 NSSM）

1. 下載 [NSSM](http://nssm.cc/download)
2. 以 **系統管理員** 身份執行：
   ```powershell
   .\deploy\deploy_windows.ps1 -NssmPath "C:\path\to\nssm.exe"
   ```
3. 服務將自動安裝並啟動（名稱：`IllumioScheduler`）

**替代方案：工作排程器**
- 建立工作 → 觸發程式：系統啟動時 → 動作：`python illumio_scheduler.py --monitor`

### Linux（Systemd）

```bash
sudo cp deploy/illumio-scheduler.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now illumio-scheduler
sudo journalctl -u illumio-scheduler -f
```

---

## 🏗️ 架構說明（開發者參考）

### 模組總覽

| 模組 | 職責 |
|---|---|
| `illumio_scheduler.py` | 程式進入點：路由至 CLI（預設）、Web GUI（`--gui`）、Daemon（`--monitor`） |
| `src/core.py` | 核心引擎：`ConfigManager`、`ScheduleDB`、`PCEClient`、`ScheduleEngine` — 零外部依賴 |
| `src/cli_ui.py` | CLI 互動選單：瀏覽/新增/修改/刪除排程、語系選擇 |
| `src/gui_ui.py` | Flask Web GUI：REST API 端點 + 內嵌 HTML/CSS/JS SPA |
| `src/i18n.py` | 國際化字串表（EN、ZH）。使用 `t('key')` 取得翻譯 |

### 核心類別（`src/core.py`）

| 類別 | 說明 |
|---|---|
| `ConfigManager` | 載入/儲存 `config.json`（PCE URL、Org ID、API Key/Secret） |
| `ScheduleDB` | JSON 格式的排程資料庫（`rule_schedules.json`） |
| `PCEClient` | Illumio PCE REST API 客戶端，使用 `urllib.request`（零依賴） |
| `ScheduleEngine` | 排程邏輯引擎：比對目前時間與排程設定，切換規則啟停狀態 |

### Web GUI API 端點（`src/gui_ui.py`）

| 路由 | 方法 | 用途 |
|---|---|---|
| `/` | GET | 提供 SPA HTML 頁面 |
| `/api/rulesets` | GET | 列出所有規則集（支援 `?q=關鍵字` 搜尋） |
| `/api/rulesets/<id>` | GET | 取得單一規則集及其規則 |
| `/api/schedules` | GET | 列出所有已設定的排程 |
| `/api/schedules` | POST | 新增或覆寫排程 |
| `/api/schedules/<href>` | DELETE | 刪除排程並清除 Note |
| `/api/check` | POST | 手動執行排程檢查 |
| `/api/config` | GET/POST | 取得或儲存 API 設定 |
| `/api/stop` | POST | 優雅關閉伺服器 |

### PCE API 整合

- **API 版本**：v2（Illumio Core 25.2+）
- **驗證方式**：HTTP Basic Auth 透過 `Authorization` 標頭
- **SSL**：停用憑證驗證（`ssl.CERT_NONE`）以相容自簽憑證
- **發布機制**：依賴感知 — 發布前呼叫 `POST /sec_policy/draft/dependencies` 探索所有必要依賴項

### 國際化系統（`src/i18n.py`）

```python
from src.i18n import t, set_lang, get_lang

set_lang('zh')        # 切換至繁體中文
set_lang('en')        # 切換至英文（預設）
print(t('app_title')) # 取得翻譯後的字串
```

新增語系：在 `_STRINGS` 字典中新增語系代碼（如 `'ja'`），填入與 `'en'` 相同的所有 key。

### 排程資料格式（`rule_schedules.json`）

```json
{
  "/orgs/1/sec_policy/draft/rule_sets/206": {
    "type": "recurring",
    "name": "K8sNode | Kubernetes",
    "is_ruleset": true,
    "action": "allow",
    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "start": "08:00",
    "end": "18:00",
    "detail_rs": "K8sNode | Kubernetes",
    "detail_src": "All",
    "detail_dst": "All",
    "detail_svc": "All",
    "detail_name": "K8sNode | Kubernetes"
  }
}
```

| 欄位 | 說明 |
|---|---|
| `type` | `recurring`（週期排程）或 `one_time`（一次性過期） |
| `is_ruleset` | `true` 排程整個規則集，`false` 排程單條規則 |
| `action` | `allow`（時段內啟動）或 `block`（時段內關閉） |
| `days` | 星期名稱陣列（如 `["Monday", "Friday"]`） |
| `start` / `end` | 時間窗口，格式 `HH:MM`（支援跨午夜） |
| `expire_at` | 一次性過期的 ISO 日期時間（如 `2025-12-31T23:59`） |

---

## ⚠️ 注意事項與疑難排解

1. **時鐘精確度** — 確認主機時區正確（`timedatectl` / Windows 時間設定）
2. **API 權限** — API Key 須具備 **Global Admin** 或 **Ruleset Provisioner** 權限
3. **發布範圍** — 本工具會自動探索依賴項，避免因缺少依賴而發布失敗
4. **檢查間隔** — 預設 300 秒，可透過環境變數 `ILLUMIO_CHECK_INTERVAL=<秒>` 調整
5. **安全性** — API 憑證以明文存於 `config.json`，請設定適當的目錄權限
6. **找不到 Flask** — 若顯示 "Flask is required"，請安裝：`pip install flask`。CLI 不需要 Flask。

---

## 📄 License

本專案為內部使用，按原樣提供。
