# Illumio 排程管理 

歡迎使用 Illumio 規則排程管理 (Rule Scheduler) 工具的使用者手冊。這份文件包含了所有關於如何設定、操作以及部署應用程式的完整指南，並附帶操作範例與運作原理解析。

## 目錄
1. [總覽與運作原理](#總覽與運作原理)
2. [操作模式](#操作模式)
    - [網頁介面 (Web GUI) 模式](#網頁介面-web-gui-模式)
    - [終端機 (CLI) 模式](#終端機-cli-模式)
    - [背景服務 (Daemon) 模式](#背景服務-daemon-模式)
3. [功能與特色](#功能與特色)
4. [連線與系統設定](#連線與系統設定)
5. [排程操作範例](#排程操作範例)
6. [部署指南](#部署指南)

---

## 總覽與運作原理
**Illumio 排程管理** 可以自動化並定時啟動與關閉 Illumio 安全性規則 (Rules) 及規則集 (RuleSets)。

### 它是如何運作的？
1. **設定目標**: 您透過介面選擇 Illumio 目標 (規則或規則集)，接著定義它們應該生效的「時間區段」或「過期下線時間」。
2. **監控引擎**: 工具會作為一個背景服務持續運行。預設情況下，每 300 秒 (5 分鐘) 引擎會自動甦醒一次來比對所有的排程設定與系統當前時間。
3. **自動切換**: 如果當前時間落在設定的排程時間區段內，引擎會透過 PCE REST API 確認目標強制設定為 `enabled=True` (開啟)。如果落在時間區段外，則強制設定為 `enabled=False` (關閉)。
4. **安全發布 (Provisioning)**: 整個程式利用了 Illumio 支援的相依性檢查機制 (Dependency-Aware)。在送出發布指令前，會安全地找出所有相依並強制必須發布的物件，避免產生惱人的「尚未發布的相依項目」錯誤。
5. **備註可視化**: Scheduler 會自動幫每個被監控的目標，加上一段文字備註 (例如 `[📅 Schedule: ...]` 或 `[⏳ Expiration: ...]`) 並寫回 PCE 上的 `description` 欄位。讓系統管理員即使登入 Illumio 本地頁面也能一目了然看見此規則目前受到排程引擎的控管。

---

## 操作模式

此程式支援三種類別的運作模式。

### 網頁介面 (Web GUI) 模式
啟動基於 Flask 驅動的全功能網頁介面以獲得最棒的視覺化體驗：
```bash
python illumio_scheduler.py --gui --port 5000
```
- **瀏覽與新增 (Browse & Add)**: 直觀搜尋導航整個系統中的規則集與細部規則，並指派排程配置給它們。左側介面面板支援寬度拖曳縮放，並全面支援滿版超寬螢幕的流暢排版。
- **已排程項目 (Schedules)**: 查看您現存的所有系統排程大表。可以選取多個項目來「批次刪除與解除排程」。
- **執行紀錄 (Logs)**: 直接嵌入在你瀏覽器中的終端機面板。利用點選 "▶ 立即執行檢查" 按鈕，可以跳過五分鐘等待時間，立刻執行並檢視除錯紀錄。
- **系統設定 (Settings)**: 安全地儲存 PCE API Token、隨時切換介面的語言 (繁體中文/英文)，以及明亮模式 (Light Mode) / 暗黑模式 (Dark Mode) 的一鍵切換。

### 終端機 (CLI) 模式
針對只有 SSH 連線且不具備桌面或瀏覽器的伺服器環境所設計。
```bash
python illumio_scheduler.py
```
執行後會進入互動式的選單：
```text
=== Illumio Scheduler ===
0. Settings
1. Schedule Management (Browse/List/Edit/Delete)
2. Run Check Now
3. Open Web GUI
q. Quit
```
在排程管理 (Schedule Management) 中，您可以敲擊字母 `a` 進入精靈面板來新增排程，也可以輸入 `e <ID>` 來編輯時間。

### 背景服務 (Daemon) 模式
長期將其投入於背景，確保不休眠的情況下時時刻刻監測系統與時間狀態。
```bash
python illumio_scheduler.py --monitor
```
*提示：請參閱 [部署指南](#部署指南) 來學習如何將其註冊成為伺服器開機常駐運行的背景服務。*

---

## 功能與特色

- **週期性排程 (Recurring Schedules)**: 設定特定一週裡的星期幾，以及對應的運行時段來允許規則存取網路。
  - *範例*: 禮拜一至禮拜五，早上 08:00 到晚上 18:00。
  - 同時也支援跨午夜的時間帶配置 (例: 22:00 ~ 06:00)。
- **一次性過期 (One-Time Expirations)**: 設定一個未來的絕對日期和時間讓規則失效下線。時間一旦抵達，這個規則就會被引擎自動關閉，並將這個排程從監測資料庫中永久清除。
- **草稿安全防護**: 排程引擎絕對不會試著把一個從沒被發布 (Provision) 出去的 草稿 (Draft) 強硬拿去做排程。
- **多語系與主題套件 (i18n & Theming)**: 從程式碼原生完美支援 繁體中文(ZH) 與 英文(EN)，且採用提取自 Illumio 品牌設計準則中的專屬色彩研發而成的明亮 (Light) 與 暗黑 (Dark) 主題雙套件。

---

## 連線與系統設定

必須要有合法的 Illumio PCE 權限認證才能取得這些資料操作，請至網頁介面或是終端機選單 #0 的設定欄中，填寫並輸入。這些機敏資料會被妥善保存在本機檔案 `config.json` 之中。

| 欄位名稱 | 涵義與說明 |
|---|---|
| **PCE URL** | 完整的 PCE FQDN 網址 (包含 Port，例如 `https://pce.local:8443`) |
| **Org ID** | 組織編號 (預設大部分企業只有單一就是填 `1`) |
| **API Key** | 由網頁 PCE 伺服器中個人大頭貼產生與頒發 (`api_123abc...`) |
| **API Secret** | 與 API Key 同步由系統產生的一段極長亂碼密碼 |

*特殊條件*: 為了確保所有權限順暢運作，您的 API Key 建立時所屬的發布者帳號，最低必須要擁抱 **Ruleset Provisioner** 管理員或是 **Global Organization Owner** 絕對負責人的權限。

---

## 排程操作範例

### 範例：一般辦公室時段控制
**情境：** 開發環境只允許在開發者進公司的白日辦公時段保持對外。
- **目標 (Target)**: 規則集 (RuleSet): `Dev Access`
- **類型 (Type)**: Recurring (每週週期性)
- **行為 (Action)**: Allow (在時段內開啟連線)
- **天數 (Days)**: Monday, Tuesday, Wednesday, Thursday, Friday (週一到週五)
- **時間**: 起點 `08:00` | 終點 `18:00`
- **最終結果**: 規則集會在週間早晨八點準時打開讓所有電腦放行，並在晚上六點之後徹底關閉阻斷任何潛在威脅。

### 範例：臨時的承包廠商開通
**情境：** 有一個承包商需要一個暫時性的遠端修復通道，月底就收回權限。
- **目標 (Target)**: 規則集 `Vendor RDP`
- **類型 (Type)**: One-Time Expiration (一次性過期)
- **過期時間**: `2025-12-31 23:59`
- **最終結果**: 這條規則的狀態會被人為開啟直到 12 月 31 號的半夜為止。跨過這個時間點的第一次掃描，這條規則會立刻被封鎖並再也不會被打開。

---

## 部署指南

為了保證極度的高可用性 (HA) 而不是只要把程式的視窗不小心關掉排程就停止，我們將會運用原廠提供的工具 `deploy/` 資料夾裡的組態安裝。

### Windows 系統
我們將利用第三方開源套件 NSSM 把 python script 封包註冊成為一個原生的 Windows 系統服務。
1. 上網下載 `nssm.exe` 放進您的任意非系統資料夾。
2. 作為 **系統管理員** 開啟 PowerShell 視窗。
3. 執行安裝腳本：
   ```powershell
   .\deploy\deploy_windows.ps1 -NssmPath "C:\path\to\nssm.exe"
   ```
4. NSSM 會幫你創造出一個名叫做 `IllumioScheduler` 且不依賴使用者的背景服務常駐。它支援自我崩潰重新開機以及記錄到事件檢視器。

### Linux 系統
我們提供標準的 Systemd 單元安裝組件腳本。
1. 先把組件設定檔送入系統：
   ```bash
   sudo cp deploy/illumio-scheduler.service /etc/systemd/system/
   ```
2. 設定開機啟動與即刻喚起：
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now illumio-scheduler
   ```
3. 下指令實時觀看服務的成功運作訊息：
   ```bash
   sudo journalctl -u illumio-scheduler -f
   ```

*本手冊結束*
