<#
.SYNOPSIS
Installs Illumio Rule Scheduler Daemon as a Windows Service using NSSM.

.DESCRIPTION
This script automates the process of setting up the Illumio Rule Scheduler 
to run continuously in the background using NSSM (Non-Sucking Service Manager).
NSSM handles auto-restart on crashes and starting the service on boot.

.PREREQUISITES
1. Python 3.8+ must be installed and in the system PATH.
2. NSSM must be downloaded and extracted.
   (Download: http://nssm.cc/download)
3. Run this script As Administrator.
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$NssmPath = "nssm.exe", # Path to nssm.exe if not in PATH

    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "IllumioScheduler",

    [Parameter(Mandatory=$false)]
    [string]$PythonExe = "python.exe" # Use full path if multiple versions exist
)

# Elevate privileges check
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "This script needs to be run as an Administrator."
    Write-Warning "Please restart PowerShell as Administrator and run again."
    break
}

# Resolve script directory (Project Root)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$MainScript = Join-Path $ProjectRoot "illumio_scheduler.py"

if (-not (Test-Path $MainScript)) {
    Write-Error "Could not find illumio_scheduler.py at $ProjectRoot"
    break
}

# Output Paths for Logs
$StdoutLog = Join-Path $ProjectRoot "daemon_stdout.log"
$StderrLog = Join-Path $ProjectRoot "daemon_stderr.log"

Write-Host "Installing Windows Service: $ServiceName" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot"
Write-Host "Main Script: $MainScript"

# Install Service
& $NssmPath install $ServiceName "$PythonExe" "`"$MainScript`" --monitor"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install service. Is NSSM in your PATH? You can provide it via -NssmPath"
    break
}

# Configure Service Directory and Logs
& $NssmPath set $ServiceName AppDirectory "$ProjectRoot"
& $NssmPath set $ServiceName AppStdout "$StdoutLog"
& $NssmPath set $ServiceName AppStderr "$StderrLog"
& $NssmPath set $ServiceName AppEnvironmentExtra "ILLUMIO_CHECK_INTERVAL=300"
& $NssmPath set $ServiceName Description "Illumio Rule Scheduler background daemon for evaluating temporary policy schedules."

Write-Host "Starting Service..." -ForegroundColor Yellow
& $NssmPath start $ServiceName

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Service '$ServiceName' installed and started successfully!" -ForegroundColor Green
    Write-Host "To view logs, check:"
    Write-Host " - $StdoutLog"
    Write-Host " - $StderrLog"
} else {
    Write-Error "`n[FAILED] Service installed but failed to start. Check Windows Event Viewer."
}
