# Run with Admin Rights
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Please run as Administrator!" -ForegroundColor Red
    exit
}

$logPath = "$env:USERPROFILE\Desktop\diagnostic_report.txt"
"System Diagnostic Report - $(Get-Date)" | Out-File $logPath

# Section 1: Resource Snapshot
"--- Resource Usage ---" | Tee-Object -Append -FilePath $logPath
Get-Process | Sort CPU -Descending | Select -First 10 | Format-Table Name, CPU, ID -AutoSize | Out-String | Tee-Object -Append -FilePath $logPath

# Section 2: Disk & RAM Status
"--- Memory Usage ---" | Tee-Object -Append -FilePath $logPath
Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory | Tee-Object -Append -FilePath $logPath

"--- Disk Usage ---" | Tee-Object -Append -FilePath $logPath
Get-PSDrive -PSProvider 'FileSystem' | Tee-Object -Append -FilePath $logPath

"--- Top 5 Disk Consuming Processes ---" | Tee-Object -Append -FilePath $logPath
Get-Process | Sort-Object IOReadBytes -Descending | Select-Object -First 5 Name, IOReadBytes | Tee-Object -Append -FilePath $logPath

# Section 3: System File Integrity
"--- Running SFC and DISM ---" | Tee-Object -Append -FilePath $logPath
Start-Process -Wait -FilePath "sfc.exe" -ArgumentList "/scannow"

DISM /Online /Cleanup-Image /ScanHealth | Tee-Object -Append -FilePath $logPath
DISM /Online /Cleanup-Image /RestoreHealth | Tee-Object -Append -FilePath $logPath

# Section 4: Startup Programs
"--- Startup Programs ---" | Tee-Object -Append -FilePath $logPath
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | Tee-Object -Append -FilePath $logPath

# Section 5: Drive Health (SMART)
"--- Disk Health (SMART Status) ---" | Tee-Object -Append -FilePath $logPath
Get-WmiObject -Namespace root\wmi -Class MSStorageDriver_FailurePredictStatus | ForEach-Object {
    "Drive: $($_.InstanceName) - PredictFailure: $($_.PredictFailure)"
} | Tee-Object -Append -FilePath $logPath

# Section 6: Optional Cleanup
"--- Cleaning Temp Files ---" | Tee-Object -Append -FilePath $logPath
$temps = @("$env:TEMP", "$env:WINDIR\Temp", "$env:LOCALAPPDATA\Temp")
foreach ($path in $temps) {
    try {
        Get-ChildItem $path -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
        "Cleaned: $path" | Tee-Object -Append -FilePath $logPath
    } catch {
        "Could not clean: $path" | Tee-Object -Append -FilePath $logPath
    }
}

"--- Finished ---" | Tee-Object -Append -FilePath $logPath
Write-Host "`nDiagnostics complete. See $logPath for results." -ForegroundColor Green
